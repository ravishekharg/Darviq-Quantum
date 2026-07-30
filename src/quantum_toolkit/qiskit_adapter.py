"""Optional Qiskit adapter (extra, not required for core functionality).

The rest of this package deliberately depends only on numpy so that
installing and testing it is fast and has no heavyweight/fragile
dependencies. This module is a thin, optional bridge showing how the same
circuits could be expressed with Qiskit instead, for readers who want to
run them on a real backend/transpiler. It is only imported if you ask for
it explicitly, and it is **not** part of the default install or test
suite -- install the ``qiskit`` extra (``pip install .[qiskit]``) to use
it.

Nothing else in ``quantum_toolkit`` imports this module.
"""

from __future__ import annotations


def _require_qiskit():
    try:
        import qiskit  # noqa: F401
        from qiskit import QuantumCircuit
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "qiskit is not installed. Install the optional extra with "
            "`pip install .[qiskit]` to use quantum_toolkit.qiskit_adapter."
        ) from exc
    return QuantumCircuit


def bernstein_vazirani_circuit(n: int, secret: int):
    """Build the equivalent Bernstein-Vazirani circuit in Qiskit, using an
    explicit ancilla qubit and phase-kickback (the "textbook" version that
    :mod:`quantum_toolkit.algorithms.bernstein_vazirani` simplifies away).
    """
    QuantumCircuit = _require_qiskit()

    qc = QuantumCircuit(n + 1, n)
    qc.x(n)  # ancilla -> |1>
    qc.h(range(n + 1))
    for i in range(n):
        if (secret >> (n - 1 - i)) & 1:
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def grover_circuit(n: int, marked: int, iterations: int):
    """Build the equivalent Grover circuit in Qiskit using a
    multi-controlled-Z oracle (via ``mcx`` conjugated with X gates on the
    zero bits of ``marked``) and the standard diffusion operator.
    """
    QuantumCircuit = _require_qiskit()

    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    zero_bits = [i for i in range(n) if not ((marked >> (n - 1 - i)) & 1)]

    for _ in range(iterations):
        # Oracle: flip phase of |marked> via a multi-controlled Z.
        for b in zero_bits:
            qc.x(b)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for b in zero_bits:
            qc.x(b)

        # Diffusion: reflect about |0...0>, sandwiched by Hadamards.
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))

    qc.measure(range(n), range(n))
    return qc
