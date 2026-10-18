import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SEED = 20261014
SAMPLE_SIZES = [100, 1000, 10000, 100000, 1000000]
GRAPHICS = Path(__file__).resolve().parents[1] / "graphics"


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



if __name__ == "__main__":
    main()
