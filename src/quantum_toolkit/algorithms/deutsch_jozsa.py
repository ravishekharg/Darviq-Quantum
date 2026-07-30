"""Deutsch-Jozsa algorithm.

Problem
-------
You are given black-box (oracle) access to a Boolean function
``f: {0,1}^n -> {0,1}`` with the *promise* that ``f`` is either:

* **constant** -- the same value for every input, or
* **balanced** -- exactly ``0`` on half the inputs and ``1`` on the other half.

Task: decide which, using as few oracle queries as possible.

Classically this requires up to ``2^(n-1) + 1`` queries in the worst case
(you could get unlucky and see the same output that many times from a
balanced function before finally seeing the other value). The
Deutsch-Jozsa algorithm solves it with a **single** quantum query,
regardless of ``n`` -- an exponential separation from the best possible
deterministic classical algorithm.

Circuit
-------
::

    |0>^n --- H^n ---[ Oracle: x -> (-1)^f(x) ]--- H^n --- measure
             (superposition)    (phase kickback)      (interference)

If ``f`` is constant, the second Hadamard layer perfectly un-does the
first, and the register returns to ``|0...0>`` with probability 1. If
``f`` is balanced, interference guarantees the amplitude of ``|0...0>``
is exactly 0, so measuring anything *other than* all-zero certifies
"balanced".

This implementation uses the phase-kickback simplification described in
:meth:`quantum_toolkit.simulator.QuantumRegister.apply_diagonal_phase`:
the oracle is applied directly as the diagonal phase ``(-1)^f(x)`` on the
``n`` data qubits, which is mathematically equivalent to the textbook
circuit with an explicit ``|-\\rangle`` ancilla.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from quantum_toolkit.simulator import QuantumRegister, parity


def constant_oracle(value: int) -> Callable[[np.ndarray], np.ndarray]:
    """``f(x) = value`` for every ``x`` (a valid *constant* oracle)."""
    if value not in (0, 1):
        raise ValueError("value must be 0 or 1")
    sign = -1.0 if value else 1.0

    def phase_fn(x: np.ndarray) -> np.ndarray:
        return np.full_like(x, sign, dtype=complex)

    return phase_fn


def balanced_oracle(secret: int) -> Callable[[np.ndarray], np.ndarray]:
    """``f(x) = parity(x & secret)`` -- balanced whenever ``secret != 0``.

    This is the same family of function used by Bernstein-Vazirani; any
    nonzero ``secret`` yields a function that is 0 on exactly half of
    ``{0,1}^n`` and 1 on the other half.
    """
    if secret == 0:
        raise ValueError("secret must be nonzero to produce a balanced function")

    def phase_fn(x: np.ndarray) -> np.ndarray:
        return np.where(parity(x & secret) == 1, -1.0, 1.0).astype(complex)

    return phase_fn


def run_deutsch_jozsa(n: int, oracle_fn: Callable[[np.ndarray], np.ndarray]) -> tuple[str, np.ndarray]:
    """Run the Deutsch-Jozsa circuit for an ``n``-qubit oracle.

    ``oracle_fn`` must be a vectorized function returning ``(-1) ** f(x)``
    for an integer array ``x`` of basis-state indices (see
    :func:`constant_oracle` / :func:`balanced_oracle`).

    Returns ``("constant" | "balanced", probabilities)``.
    """
    reg = QuantumRegister(n)
    reg.h_all()
    reg.apply_diagonal_phase(oracle_fn)
    reg.h_all()

    probs = reg.probabilities()
    verdict = "constant" if np.isclose(probs[0], 1.0, atol=1e-9) else "balanced"
    return verdict, probs
