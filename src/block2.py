import random


SEED = 20261014


def ratio(numerator, denominator):
    """Умовна частота не визначена, якщо подія-умова не трапилася."""
    if denominator == 0:
        return None
    return numerator / denominator


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


def main():
    rows, checks = block2()
    names = ["A", "B", "A∩B", "A∪B", "A|B", "B|A", "A|(A∪B)"]
    print("Блок 2. Незалежні відмови маршрутизаторів. Варіант 1")
    print("Кількість днів: 100000")
    print("Подія; теорія; частота; абсолютна похибка")
    for index in range(len(rows)):
        row = rows[index]
        print(f"{names[index]}; {row['theory']:.7f}; "
              f"{row['estimate']:.7f}; {row['abs_error']:.7f}")
    print(f"M(A)={checks['M_A']}; M(B)={checks['M_B']}; "
          f"M(A∩B)={checks['M_AB']}; M(A∪B)={checks['M_union']}")
    print(f"Перевірка додавання: різниця = {checks['addition_gap']:.10f}")
    print(f"Перевірка множення: різниця = {checks['multiplication_gap']:.10f}")
    print(f"W(A∩B) − W(A)W(B) = {checks['independence_gap']:.10f}")
    print(f"Доступність вузла: теорія {checks['node_availability_theory']:.6f}; "
          f"частота {checks['node_availability_estimate']:.6f}")


if __name__ == "__main__":
    main()
