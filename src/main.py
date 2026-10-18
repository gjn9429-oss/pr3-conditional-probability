import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from block2 import main as run_block_2


SEED = 20261014
SAMPLE_SIZES = [100, 1000, 10000, 100000, 1000000]
GRAPHICS = Path(__file__).resolve().parents[1] / "graphics"


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
    unavailable = [0, 0, 0]

    for _ in range(total):
        service1 = generator.random() < 0.99
        service2 = generator.random() < 0.98
        service3 = generator.random() < 0.95
        # Окремо враховуємо всі недоступні сервіси, навіть при спільних відмовах.
        if not service1:
            unavailable[0] += 1
        if not service2:
            unavailable[1] += 1
        if not service3:
            unavailable[2] += 1
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
                     "unavailable_count": unavailable[index],
                     "unavailable_frequency": unavailable[index] / total,
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


def run_block_1():
    rows = block1()
    GRAPHICS.mkdir(exist_ok=True)
    convergence_plot(rows, "W_B_given_A", "abs_error_B_given_A", 0.75,
                     "Частота W(B|A)", "block1_convergence.png")

    print("Блок 1. Умовна ймовірність запитів до БД")
    print("Теорія: P(A)=0.28; P(B)=0.30; P(A∩B)=0.21")
    print("P(A|B)=0.70; P(B|A)=0.75. Події A і B залежні.")
    print("N; W(A); W(B); W(A∩B); W(A|B); W(B|A); абсолютна похибка P(B|A)")
    for row in rows:
        print(f"{row['N']}; {row['W_A']:.6f}; {row['W_B']:.6f}; "
              f"{row['W_AB']:.6f}; {row['W_A_given_B']:.6f}; "
              f"{row['W_B_given_A']:.6f}; {row['abs_error_B_given_A']:.6f}")
    last = rows[-1]
    print(f"W(A∩B) − W(A)W(B) = {last['independence_gap']:.8f}")
    print("Графік: graphics/block1_convergence.png")


def run_block_3():
    rows = block3()
    GRAPHICS.mkdir(exist_ok=True)
    convergence_plot(rows, "estimate", "abs_error", rows[0]["theory"],
                     "Надійність W системи", "block3_convergence.png")
    print("Блок 3. Надійність серійно-паралельної вебсистеми")
    print("N; теорія; частота; абсолютна похибка")
    for row in rows:
        print(f"{row['N']}; {row['theory']:.7f}; "
              f"{row['estimate']:.7f}; {row['abs_error']:.7f}")
    print("Графік: graphics/block3_convergence.png")


def run_block_4():
    fourth, summary = block4()
    GRAPHICS.mkdir(exist_ok=True)
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

    print("Блок 4. Надійність трьох послідовних мікросервісів. Варіант 1")
    print(f"Кількість запитів: {summary['N']}")
    print(f"Точна доступність: {summary['theory']:.5f}")
    print(f"Успішних запитів: {summary['successes']}; відмов: {summary['failures']}")
    print(f"Частота успіху: {summary['estimate']:.6f}; "
          f"абсолютна похибка: {summary['abs_error']:.6f}")
    print("Перший недоступний сервіс; кількість; теорія; частка всіх; частка невдалих")
    for row in fourth:
        print(f"{row['service']}; {row['first_failure_count']}; "
              f"{row['theory_cause']:.6f}; {row['fraction_all_requests']:.6f}; "
              f"{row['fraction_failed_requests']:.6f}")
    print("Недоступність кожного сервісу (події можуть перетинатися):")
    for row in fourth:
        print(f"{row['service']}; {row['unavailable_count']}; "
              f"{row['unavailable_frequency']:.6f}")
    print("Графік: graphics/block4_failures.png")


def main():
    # Послідовно запускаємо чотири блоки практичної роботи.
    run_block_1()
    print()
    run_block_2()
    print()
    run_block_3()
    print()
    run_block_4()


if __name__ == "__main__":
    main()
