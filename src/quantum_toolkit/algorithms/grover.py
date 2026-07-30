"""Grover's search algorithm.

Problem
-------
You have oracle access to a function that marks exactly one item out of
``N = 2^n`` unstructured items (e.g. "is this the item we're looking
for?"). Find the marked item.

Classically, unstructured search needs ``O(N)`` oracle queries on
average (there's no structure to exploit, so you just check items one
by one). Grover's algorithm finds the marked item with high probability
using only ``O(sqrt(N))`` queries -- a quadratic speedup -- by rotating
the statevector towards the marked basis state through repeated
"amplitude amplification".

Circuit (one iteration)
-----------------------
::

    |0>^n --- H^n ---[ Oracle: flip sign of |marked> ]---[ Diffusion ]--- ... repeat ~pi/4*sqrt(N) times ... --- measure

    Diffusion operator D = H^n . (2|0><0| - I) . H^n
                          = reflect about |0...0>, sandwiched by Hadamards
                          = reflection about the mean amplitude (2|s><s| - I)

Each Grover iteration = oracle reflection + diffusion reflection, which
together rotate the statevector by a fixed angle in the 2D plane spanned
by the marked state and the uniform superposition over the rest. After
approximately ``iterations = round(pi/4 * sqrt(N))`` iterations, the
amplitude (and hence measurement probability) of the marked state is
maximized.
"""

from __future__ import annotations

import math
from typing import Optional

from quantum_toolkit.simulator import QuantumRegister, bitstring


def optimal_iterations(n: int) -> int:
    """Theoretically optimal number of Grover iterations for ``n`` qubits
    (a single marked item out of ``N = 2**n``).

    The well-known asymptotic estimate is ``round(pi/4 * sqrt(N))``, and
    that's an excellent approximation once ``N`` is reasonably large.
    Geometrically, though, each iteration rotates the statevector by a
    fixed angle ``theta = 2*asin(1/sqrt(N))`` towards the marked state, and
    the *exact* optimal integer iteration count is the one that lands
    closest to a total rotation of ``pi/2`` (maximum overlap with the
    marked state):  ``k* = round(pi / (2*theta) - 1/2)``. For small ``N``
    (e.g. ``N=4``) this exact formula and the asymptotic ``pi/4*sqrt(N)``
    estimate can disagree by one iteration -- rounding ``pi/4*sqrt(N)``
    naively can overshoot the true optimum and noticeably hurt the success
    probability. We use the exact formula here; it converges to the
    ``pi/4*sqrt(N)`` estimate as ``N`` grows.
    """
    N = 2 ** n
    theta = 2.0 * math.asin(1.0 / math.sqrt(N))
    k = round((math.pi / (2.0 * theta)) - 0.5)
    return max(1, k)


def _diffusion(reg: QuantumRegister) -> QuantumRegister:
    """Apply the Grover diffusion operator ``2|s><s| - I`` via its standard
    decomposition: ``H^n``, reflect about ``|0...0>``, ``H^n``.
    """
    reg.h_all()
    reg.amps[0] *= -1.0
    reg.h_all()
    return reg


def grover_search(n: int, marked: int, iterations: Optional[int] = None) -> tuple[QuantumRegister, int]:
    """Run Grover's algorithm over ``n`` qubits with a single marked basis
    state ``marked`` (an int in ``[0, 2**n)``).

    If ``iterations`` is not given, uses the theoretically optimal count
    from :func:`optimal_iterations`.

    Returns ``(register, iterations_used)``.
    """
    N = 2 ** n
    if not (0 <= marked < N):
        raise ValueError(f"marked item {marked} does not fit in {n} qubits")
    if iterations is None:
        iterations = optimal_iterations(n)

    reg = QuantumRegister(n)
    reg.h_all()

    for _ in range(iterations):
        # Oracle: flip the phase of exactly the marked basis state. This is
        # the diagonal unitary equivalent of a multi-controlled-Z gate
        # conditioned on the bit pattern of `marked`.
        reg.amps[marked] *= -1.0
        _diffusion(reg)

    return reg, iterations


def run_grover(n: int, marked_bitstring: str, iterations: Optional[int] = None):
    """Convenience wrapper: run Grover's search for a marked bitstring and
    return ``(found_bitstring, probability_of_marked, iterations_used)``.
    """
    marked = int(marked_bitstring, 2)
    reg, used_iterations = grover_search(n, marked, iterations)
    probs = reg.probabilities()
    found_index = reg.most_probable()
    return bitstring(found_index, n), float(probs[marked]), used_iterations
