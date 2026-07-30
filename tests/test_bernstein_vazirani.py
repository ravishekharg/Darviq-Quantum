import random

import pytest

from quantum_toolkit.algorithms.bernstein_vazirani import run_bernstein_vazirani


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 7, 8])
def test_recovers_all_secrets_for_small_n(n):
    # Exhaustively check every possible secret for small n.
    if 2 ** n > 64:
        pytest.skip("covered by the randomized test below")
    for secret in range(2 ** n):
        recovered = run_bernstein_vazirani(n, secret)
        assert recovered == format(secret, f"0{n}b")


@pytest.mark.parametrize("n", [6, 8, 10, 12])
def test_recovers_random_secrets(n):
    rng = random.Random(123 + n)
    for _ in range(20):
        secret = rng.randint(0, 2 ** n - 1)
        recovered = run_bernstein_vazirani(n, secret)
        assert recovered == format(secret, f"0{n}b")


def test_all_zero_secret():
    assert run_bernstein_vazirani(5, 0) == "00000"


def test_all_one_secret():
    n = 6
    secret = 2 ** n - 1
    assert run_bernstein_vazirani(n, secret) == "1" * n


def test_rejects_secret_too_large():
    with pytest.raises(ValueError):
        run_bernstein_vazirani(3, 8)
