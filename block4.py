import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SEED = 20261014
GRAPHICS = Path(__file__).resolve().parent / "graphics"


def ratio(numerator, denominator):
    """Умовна частота не визначена, якщо подія-умова не трапилася."""
    if denominator == 0:
        return None
    return numerator / denominator


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


def main():
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
    print("Графік: graphics/block4_failures.png")


if __name__ == "__main__":
    main()
