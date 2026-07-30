"""Bernstein-Vazirani algorithm.

Problem
-------
You are given black-box access to ``f(x) = x . s (mod 2)`` (bitwise dot
product / parity), for some hidden ``n``-bit secret string ``s``. Recover
``s``.

Classically this needs ``n`` queries (probe each standard basis vector
``e_i`` to peel off ``s_i`` one bit at a time). Bernstein-Vazirani
recovers the *entire* string ``s`` with a **single** quantum query -- an
``O(n)`` -> ``O(1)`` query-complexity separation.

Circuit
-------
::

    |0>^n --- H^n ---[ Oracle: x -> (-1)^(x.s) ]--- H^n --- measure --> s

Measuring the register after the second Hadamard layer yields the
secret string ``s`` directly, with probability 1 (no repetition needed).
As with the Deutsch-Jozsa module, the oracle is applied as the diagonal
phase-kickback ``(-1)^(x . s)`` rather than materializing an explicit
ancilla qubit.
"""

from __future__ import annotations

import numpy as np

from quantum_toolkit.simulator import QuantumRegister, bitstring, parity


def run_bernstein_vazirani(n: int, secret: int) -> str:
    """Recover an ``n``-bit secret ``s`` (given here as an int) in one query.

    Returns the recovered secret as an ``n``-bit binary string.
    """
    if not (0 <= secret < 2 ** n):
        raise ValueError(f"secret {secret} does not fit in {n} bits")

    reg = QuantumRegister(n)
    reg.h_all()
    reg.apply_diagonal_phase(lambda x: np.where(parity(x & secret) == 1, -1.0, 1.0).astype(complex))
    reg.h_all()

    recovered_index = reg.most_probable()
    # The algorithm is exact: probability at the secret index should be 1.
    return bitstring(recovered_index, n)
