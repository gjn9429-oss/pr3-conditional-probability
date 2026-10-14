"""Незалежна перевірка формул перебором станів і контроль CSV/JSON."""

import json
import math
from fractions import Fraction
from itertools import product
from pathlib import Path


def state_probability(states, probabilities):
    result = Fraction(1)
    for state, probability in zip(states, probabilities):
        result *= probability if state else 1 - probability
    return result


def close(actual, expected):
    assert math.isclose(actual, float(expected), rel_tol=0, abs_tol=1e-12), (actual, expected)


def verify():
    data = json.loads((Path(__file__).parent / "results/results.json").read_text(encoding="utf-8"))
    # Перебір 32 станів дає точну надійність вебсистеми незалежно від формули main.py.
    probabilities = [Fraction(98, 100), Fraction(9, 10), Fraction(9, 10), Fraction(95, 100), Fraction(95, 100)]
    web_exact = Fraction(0)
    for states in product([False, True], repeat=5):
        lb, web1, web2, db1, db2 = states
        if lb and (web1 or web2) and (db1 or db2):
            web_exact += state_probability(states, probabilities)
    close(web_exact, Fraction(1935549, 2000000))

    # Усі 8 станів мікросервісів і взаємовиключні перші причини відмови.
    service_probs = [Fraction(99, 100), Fraction(98, 100), Fraction(95, 100)]
    service_exact = Fraction(0)
    cause_exact = [Fraction(0), Fraction(0), Fraction(0)]
    for states in product([False, True], repeat=3):
        probability = state_probability(states, service_probs)
        if all(states):
            service_exact += probability
        else:
            cause_exact[states.index(False)] += probability
    close(service_exact, Fraction(92169, 100000))
    close(service_exact + sum(cause_exact), 1)

    # Чотири комбінації маршрутизаторів.
    router_probs = [Fraction(15, 100), Fraction(10, 100)]
    joint = union = Fraction(0)
    for states in product([False, True], repeat=2):
        probability = state_probability(states, router_probs)
        if all(states):
            joint += probability
        if any(states):
            union += probability
    expected_router = [router_probs[0], router_probs[1], joint, union,
                       joint / router_probs[1], joint / router_probs[0], router_probs[0] / union]
    for row, expected in zip(data["block2"], expected_router):
        close(row["theory"], expected)
        close(row["abs_error"], abs(row["estimate"] - float(expected)))

    # Контроль частот і знаменників умовних оцінок.
    for row in data["block1"]:
        n = row["N"]
        assert 0 <= row["M_AB"] <= min(row["M_A"], row["M_B"]) <= n
        close(row["W_A"], row["M_A"] / n)
        close(row["W_B"], row["M_B"] / n)
        close(row["W_AB"], row["M_AB"] / n)
        close(row["W_A_given_B"], row["M_AB"] / row["M_B"])
        close(row["W_B_given_A"], row["M_AB"] / row["M_A"])
    checks = data["block2_checks"]
    assert checks["M_union"] == checks["M_A"] + checks["M_B"] - checks["M_AB"]
    close(checks["addition_gap"], 0)
    close(checks["multiplication_gap"], 0)
    for row in data["block3"]:
        close(row["theory"], web_exact)
        assert row["successes"] + row["failures"] == row["N"]
        close(row["estimate"], row["successes"] / row["N"])
    summary = data["block4_summary"]
    close(summary["theory"], service_exact)
    assert summary["successes"] + summary["failures"] == summary["N"]
    assert sum(row["first_failure_count"] for row in data["block4"]) == summary["failures"]
    for row, expected in zip(data["block4"], cause_exact):
        close(row["theory_cause"], expected)

    # Шість стандартних відхилень — лише перевірка грубої помилки симуляції.
    # Це не вимога методички та не доказ рівності частоти й точного значення.
    sanity_cases = [(data["block3"][-1]["estimate"], float(web_exact), 1000000),
                    (summary["estimate"], float(service_exact), 100000)]
    for estimate, exact, n in sanity_cases:
        assert abs(estimate - exact) < 6 * math.sqrt(exact * (1 - exact) / n)
    print("Перевірено: 32 стани вебсистеми, 8 станів мікросервісів, 4 стани маршрутизаторів.")
    print("Перевірено лічильники, умовні частоти, похибки та теореми. Усі перевірки пройшли.")


if __name__ == "__main__":
    verify()
