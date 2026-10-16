"""Практична робота № 5–6. Варіант 1. Римаренко Євгеній, ІВ-25-1."""

import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SEED = 20261014
SAMPLE_SIZES = [100, 1000, 10000, 100000, 1000000]
GRAPHICS = Path(__file__).resolve().parent.parent / "graphics"


def ratio(numerator, denominator):
    """Умовна частота не визначена, якщо подія-умова не трапилася."""
    if denominator == 0:
        return None
    return numerator / denominator



def block1():
    """B — складний JOIN-запит, A — затримка понад 200 мс."""
    generator = random.Random(SEED + 1)
    count_a = 0
    count_b = 0
    count_ab = 0
    rows = []

    # Один експеримент: таблиця містить результати його перших N запитів.
    for number in range(1, SAMPLE_SIZES[-1] + 1):
        complex_query = generator.random() < 0.30
        if complex_query:
            slow_query = generator.random() < 0.70
        else:
            slow_query = generator.random() < 0.10

        if slow_query:
            count_a += 1
        if complex_query:
            count_b += 1
        if slow_query and complex_query:
            count_ab += 1

        if number in SAMPLE_SIZES:
            b_given_a = ratio(count_ab, count_a)
            row = {
                "N": number, "M_A": count_a, "M_B": count_b,
                "M_AB": count_ab, "W_A": count_a / number,
                "W_B": count_b / number, "W_AB": count_ab / number,
                "W_A_given_B": ratio(count_ab, count_b),
                "W_B_given_A": b_given_a,
                "abs_error_B_given_A": None if b_given_a is None else abs(b_given_a - 0.75),
                "independence_gap": count_ab / number - (count_a / number) * (count_b / number),
            }
            rows.append(row)

    return rows


def block2():
    """Незалежні відмови маршрутизаторів: A — R1, B — R2."""
    generator = random.Random(SEED + 2)
    total = 100000
    count_a = count_b = count_ab = count_union = 0

    for _ in range(total):
        failed_r1 = generator.random() < 0.15
        failed_r2 = generator.random() < 0.10
        if failed_r1:
            count_a += 1
        if failed_r2:
            count_b += 1
        if failed_r1 and failed_r2:
            count_ab += 1
        if failed_r1 or failed_r2:
            count_union += 1

    p_a = 0.15
    p_b = 0.10
    p_ab = p_a * p_b
    p_union = p_a + p_b - p_ab
    theory = [p_a, p_b, p_ab, p_union, p_a, p_b, p_a / p_union]
    estimates = [count_a / total, count_b / total, count_ab / total,
                 count_union / total, ratio(count_ab, count_b),
                 ratio(count_ab, count_a), ratio(count_a, count_union)]
    events = ["A", "B", "A_intersect_B", "A_union_B", "A_given_B", "B_given_A", "A_given_union"]
    rows = []
    for event, exact, estimate in zip(events, theory, estimates):
        rows.append({"event": event, "N": total, "theory": exact,
                     "estimate": estimate, "abs_error": abs(estimate - exact)})

    checks = {
        "M_A": count_a, "M_B": count_b, "M_AB": count_ab, "M_union": count_union,
        "addition_gap": estimates[3] - (estimates[0] + estimates[1] - estimates[2]),
        "multiplication_gap": estimates[2] - estimates[1] * estimates[4],
        "independence_gap": estimates[2] - estimates[0] * estimates[1],
        "node_availability_theory": 1 - p_ab,
        "node_availability_estimate": 1 - estimates[2],
    }
    return rows, checks


def block3():
    """LB та дві паралельні підсистеми: Web1/Web2 і DB1/DB2."""
    generator = random.Random(SEED + 3)
    exact = 0.98 * (1 - 0.10 * 0.10) * (1 - 0.05 * 0.05)
    successes = 0
    rows = []

    for number in range(1, SAMPLE_SIZES[-1] + 1):
        # Генеруємо всі компоненти окремо, до перевірки логіки системи.
        lb = generator.random() < 0.98
        web1 = generator.random() < 0.90
        web2 = generator.random() < 0.90
        db1 = generator.random() < 0.95
        db2 = generator.random() < 0.95
        system_ok = lb and (web1 or web2) and (db1 or db2)
        if system_ok:
            successes += 1

        if number in SAMPLE_SIZES:
            estimate = successes / number
            rows.append({"N": number, "successes": successes,
                         "failures": number - successes, "theory": exact,
                         "estimate": estimate, "abs_error": abs(estimate - exact)})

    return rows


def block4():
    """Три послідовні мікросервіси. Причина — перший недоступний сервіс."""
    generator = random.Random(SEED + 4)
    total = 100000
    successes = 0
    failures = [0, 0, 0]

    for _ in range(total):
        service1 = generator.random() < 0.99
        service2 = generator.random() < 0.98
        service3 = generator.random() < 0.95
        # Кожному невдалому запиту приписуємо тільки першу причину.
        if not service1:
            failures[0] += 1
        elif not service2:
            failures[1] += 1
        elif not service3:
            failures[2] += 1
        else:
            successes += 1

    exact_causes = [0.01, 0.99 * 0.02, 0.99 * 0.98 * 0.05]
    rows = []
    failed_total = sum(failures)
    for index in range(3):
        estimate = failures[index] / total
        rows.append({"service": f"S{index + 1}", "first_failure_count": failures[index],
                     "theory_cause": exact_causes[index], "fraction_all_requests": estimate,
                     "fraction_failed_requests": ratio(failures[index], failed_total),
                     "abs_error": abs(estimate - exact_causes[index])})

    summary = {"N": total, "successes": successes, "failures": failed_total,
               "theory": 0.99 * 0.98 * 0.95, "estimate": successes / total,
               "abs_error": abs(successes / total - 0.99 * 0.98 * 0.95)}
    return rows, summary


def convergence_plot(rows, estimate_key, error_key, exact, ylabel, filename):
    sizes = [row["N"] for row in rows]
    estimates = [row[estimate_key] for row in rows]
    errors = [row[error_key] for row in rows]
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(sizes, estimates, "o-", label="Статистична оцінка")
    axes[0].axhline(exact, color="darkred", linestyle="--", label=f"Теорія: {exact:.7g}")
    axes[0].set_ylabel(ylabel)
    axes[0].legend()
    axes[1].plot(sizes, errors, "o-", color="darkgreen")
    axes[1].set_ylabel("Абсолютна похибка")
    for axis in axes:
        axis.set_xscale("log")
        axis.set_xlabel("Кількість випробувань N")
        axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(GRAPHICS / filename, dpi=300)
    plt.close(figure)


def main():
    GRAPHICS.mkdir(exist_ok=True)
    first = block1()
    second, second_checks = block2()
    third = block3()
    fourth, fourth_summary = block4()
    convergence_plot(first, "W_B_given_A", "abs_error_B_given_A", 0.75,
                     "Частота W(B|A)", "block1_convergence.png")
    convergence_plot(third, "estimate", "abs_error", third[0]["theory"],
                     "Надійність W системи", "block3_convergence.png")

    figure, axis = plt.subplots(figsize=(7, 4))
    positions = [0, 1, 2]
    axis.bar([x - 0.18 for x in positions], [row["theory_cause"] for row in fourth],
             width=0.36, label="Теорія")
    axis.bar([x + 0.18 for x in positions], [row["fraction_all_requests"] for row in fourth],
             width=0.36, label="Симуляція")
    axis.set_xticks(positions, ["Сервіс S1", "Сервіс S2", "Сервіс S3"])
    axis.set_ylabel("Частка від усіх запитів")
    axis.set_title("Перша причина відмови ланцюжка")
    axis.legend()
    axis.grid(axis="y", alpha=0.3)
    figure.tight_layout()
    figure.savefig(GRAPHICS / "block4_failures.png", dpi=300)
    plt.close(figure)

    lines = ["Практична робота № 5–6, варіант 1", f"Зерно генератора: {SEED}",
             "Блок 1: N; W(A); W(B); W(A∩B); W(A|B); W(B|A); абсолютна похибка"]
    for row in first:
        lines.append(f"{row['N']}; {row['W_A']:.6f}; {row['W_B']:.6f}; {row['W_AB']:.6f}; "
                     f"{row['W_A_given_B']:.6f}; {row['W_B_given_A']:.6f}; {row['abs_error_B_given_A']:.6f}")
    lines.append("Блок 2: подія; теорія; частота; абсолютна похибка")
    for row in second:
        lines.append(f"{row['event']}; {row['theory']:.7f}; {row['estimate']:.7f}; {row['abs_error']:.7f}")
    lines.append("Блок 3: N; теорія; частота; абсолютна похибка")
    for row in third:
        lines.append(f"{row['N']}; {row['theory']:.7f}; {row['estimate']:.7f}; {row['abs_error']:.7f}")
    lines.append(f"Блок 4: успішних запитів {fourth_summary['successes']}; "
                 f"відмов {fourth_summary['failures']}; "
                 f"доступність {fourth_summary['estimate']:.6f}; "
                 f"похибка {fourth_summary['abs_error']:.6f}")
    for row in fourth:
        lines.append(f"{row['service']}: перших відмов {row['first_failure_count']}; "
                     f"частка всіх запитів {row['fraction_all_requests']:.6f}; "
                     f"частка невдалих {row['fraction_failed_requests']:.6f}")
    lines.append(f"Графіки збережено в: {GRAPHICS}")
    console = "\n".join(lines)
    print(console)


if __name__ == "__main__":
    main()
