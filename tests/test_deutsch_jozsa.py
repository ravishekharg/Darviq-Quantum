import random

import pytest

from quantum_toolkit.algorithms.deutsch_jozsa import balanced_oracle, constant_oracle, run_deutsch_jozsa


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize("value", [0, 1])
def test_constant_oracle_detected(n, value):
    verdict, probs = run_deutsch_jozsa(n, constant_oracle(value))
    assert verdict == "constant"
    assert probs[0] == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
def test_balanced_oracle_detected_across_random_secrets(n):
    rng = random.Random(42 + n)
    for _ in range(8):
        secret = rng.randint(1, 2 ** n - 1)
        verdict, probs = run_deutsch_jozsa(n, balanced_oracle(secret))
        assert verdict == "balanced", f"failed for n={n}, secret={secret:0{n}b}"
        assert probs[0] == pytest.approx(0.0, abs=1e-9)


def test_constant_oracle_rejects_bad_value():
    with pytest.raises(ValueError):
        constant_oracle(2)


def test_balanced_oracle_rejects_zero_secret():
    with pytest.raises(ValueError):
        balanced_oracle(0)


def test_probabilities_sum_to_one():
    verdict, probs = run_deutsch_jozsa(5, balanced_oracle(7))
    assert probs.sum() == pytest.approx(1.0, abs=1e-9)
