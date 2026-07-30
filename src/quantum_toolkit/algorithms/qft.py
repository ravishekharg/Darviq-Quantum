"""Quantum Fourier Transform (QFT).

Problem
-------
The QFT is the quantum analogue of the discrete Fourier transform (DFT):
given amplitudes ``x_0 ... x_{N-1}`` (``N = 2^n``) it produces

::

    X_k = (1/sqrt(N)) * sum_j  x_j * exp(2*pi*i*j*k / N)

Classically, computing a DFT on a length-``N`` vector takes ``O(N log N)``
time with the FFT. The *quantum* Fourier transform computes the same
linear transform on the amplitudes of an ``n``-qubit register using only
``O(n^2)`` gates (``O(n)`` Hadamards and ``O(n^2)`` controlled-phase
rotations) -- exponentially fewer gates than classical FFT operations,
though the caveat is that you can never read out all ``N`` transformed
amplitudes directly (measurement collapses the state). The QFT is the
core subroutine behind Shor's factoring algorithm and quantum phase
estimation.

Circuit (n=3 shown, textbook construction)
-------------------------------------------
::

    q0: --H--o--------o----------------x---
              |        |                |
    q1: -----P(pi/2)--|----H--o---------|---
                       |       |         |
    q2: ---------------P(pi/4)-P(pi/2)--H--x--- (then swap q0 <-> q2)

Each qubit gets a Hadamard followed by controlled-phase rotations
conditioned on every qubit "below" it, with angles halving each step;
a final layer of swaps reverses the qubit order to match the standard
output convention. This module implements exactly that construction
gate-by-gate (no shortcuts), and the test suite verifies the resulting
statevector transform against ``numpy.fft`` computed directly on the
input amplitudes.
"""

from __future__ import annotations

import math

import numpy as np

from quantum_toolkit.simulator import QuantumRegister


def apply_qft(reg: QuantumRegister, swap_output: bool = True) -> QuantumRegister:
    """Apply the QFT circuit in place to ``reg`` and return it.

    ``swap_output=True`` (the default) reverses the qubit order at the end,
    which is the standard convention that makes the QFT statevector equal
    (up to normalization) to ``numpy.fft.ifft`` of the input amplitudes.
    """
    n = reg.n
    for j in range(n):
        reg.h(j)
        for k in range(j + 1, n):
            theta = math.pi / (2 ** (k - j))
            reg.cphase(k, j, theta)

    if swap_output:
        for j in range(n // 2):
            reg.swap(j, n - 1 - j)

    return reg


def qft(amplitudes: np.ndarray, swap_output: bool = True) -> np.ndarray:
    """Apply the QFT to an arbitrary (normalized) amplitude vector of
    length ``2**n`` and return the transformed amplitudes.
    """
    n = int(round(math.log2(len(amplitudes))))
    reg = QuantumRegister(n, amplitudes)
    apply_qft(reg, swap_output=swap_output)
    return reg.amps


def classical_dft_reference(amplitudes: np.ndarray) -> np.ndarray:
    """The classical statevector this QFT *should* produce, computed with
    ``numpy.fft`` directly on the amplitude vector for cross-checking.

    QFT|j> = (1/sqrt(N)) sum_k exp(2*pi*i*j*k/N) |k>, which is exactly
    ``sqrt(N) * numpy.fft.ifft(amplitudes)`` (ifft carries the ``1/N``
    normalization and the ``+i`` sign convention that matches the QFT).
    """
    N = len(amplitudes)
    return math.sqrt(N) * np.fft.ifft(amplitudes)
