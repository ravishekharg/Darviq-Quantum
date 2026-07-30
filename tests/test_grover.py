import math
import random

import pytest

from quantum_toolkit.algorithms.grover import grover_search, optimal_iterations, run_grover


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
def test_finds_marked_item_with_high_probability(n):
    rng = random.Random(7 + n)
    N = 2 ** n
    for _ in range(5):
        marked = rng.randint(0, N - 1)
        found, prob_marked, iterations = run_grover(n, format(marked, f"0{n}b"))
        assert found == format(marked, f"0{n}b")
        # Grover's success probability is high but not exactly 1 for finite n;
        # for a single marked item it should comfortably exceed 0.9 except at
        # very small N where the rounded iteration count is coarse.
        assert prob_marked > 0.85, f"n={n} marked={marked} prob={prob_marked}"


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 8])
def test_iteration_count_matches_theoretical_optimum(n):
    # The exact optimal iteration count (used internally) should stay close
    # to the well-known asymptotic estimate pi/4 * sqrt(N); they can differ
    # by at most one iteration for small N, and converge as N grows.
    N = 2 ** n
    asymptotic_estimate = max(1, round((math.pi / 4.0) * math.sqrt(N)))
    actual = optimal_iterations(n)
    assert abs(actual - asymptotic_estimate) <= 1

    _, _, used = run_grover(n, "0" * n)
    assert used == actual


def test_grover_search_rejects_out_of_range_marked_item():
    with pytest.raises(ValueError):
        grover_search(3, 8)


def test_custom_iteration_count_is_honored():
    _, _, used = run_grover(4, "1010", iterations=3)
    assert used == 3


def test_more_iterations_than_optimal_can_reduce_success_probability():
    # Sanity check on the oscillatory nature of Grover's algorithm: driving
    # far past the optimal iteration count should not simply keep improving
    # the probability of measuring the marked state -- it should have fallen
    # from its near-peak value at the optimum.
    n = 6
    marked = "101010"
    _, prob_optimal, opt_iters = run_grover(n, marked)
    _, prob_overshoot, _ = run_grover(n, marked, iterations=opt_iters * 4)
    assert prob_optimal > 0.9
    assert prob_overshoot < prob_optimal
