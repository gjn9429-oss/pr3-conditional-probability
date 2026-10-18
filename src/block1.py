import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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



if __name__ == "__main__":
    main()
