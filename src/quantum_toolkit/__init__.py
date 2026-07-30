"""quantum_toolkit: a small, dependency-light (numpy-only) statevector
quantum simulator plus a handful of canonical quantum algorithms.

This package intentionally avoids pulling in a full quantum SDK (Qiskit,
Cirq, ...) for its core functionality. Instead it implements a minimal
statevector simulator directly on top of numpy arrays. This keeps install
and CI times fast and keeps the linear-algebra behind each algorithm
transparent and easy to read.

See ``quantum_toolkit.simulator`` for the simulator core and
``quantum_toolkit.algorithms`` for the algorithm implementations.
"""

__version__ = "0.1.0"
