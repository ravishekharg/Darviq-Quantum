"""A minimal numpy-only statevector simulator.

Convention
----------
An ``n``-qubit register is a complex vector of length ``2**n``. Basis state
index ``i`` corresponds to the computational basis ket ``|q0 q1 ... q_{n-1}>``
where ``q0`` is the *most significant* bit of ``i`` (i.e. qubit 0 is drawn
left-most, matching standard textbook notation and numpy's row-major
``reshape`` order). This convention is used consistently by every gate,
oracle, and algorithm in this package.

Gates are applied by reshaping the flat state vector into an ``n``-index
tensor of shape ``(2,) * n``, permuting the target qubit axes to the front,
contracting with the (small, dense) gate matrix, and permuting back. This
lets a single ``apply_gate`` routine implement single-qubit gates,
controlled gates, and any other small multi-qubit gate without writing a
separate exponentially-sized matrix for the whole register.
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Standard gate matrices
# ---------------------------------------------------------------------------

I2 = np.eye(2, dtype=complex)

H = (1.0 / np.sqrt(2.0)) * np.array([[1, 1], [1, -1]], dtype=complex)

X = np.array([[0, 1], [1, 0]], dtype=complex)

Y = np.array([[0, -1j], [1j, 0]], dtype=complex)

Z = np.array([[1, 0], [0, -1]], dtype=complex)


def phase_gate(theta: float) -> np.ndarray:
    """Single-qubit phase gate ``diag(1, e^{i theta})``."""
    return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)


# Two-qubit gates, given as 4x4 matrices acting on qubits ``[control, target]``
# (control is the "outer"/more-significant axis of the pair).
CNOT = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=complex,
)

CZ = np.diag([1, 1, 1, -1]).astype(complex)

SWAP = np.array(
    [
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
    ],
    dtype=complex,
)


def controlled_phase(theta: float) -> np.ndarray:
    """Two-qubit controlled-phase gate ``diag(1, 1, 1, e^{i theta})``."""
    return np.diag([1, 1, 1, np.exp(1j * theta)]).astype(complex)


# ---------------------------------------------------------------------------
# Bit utilities (vectorized popcount / parity over numpy integer arrays)
# ---------------------------------------------------------------------------


def popcount(x: np.ndarray) -> np.ndarray:
    """Vectorized population count (number of set bits) for uint64 arrays."""
    x = np.asarray(x).astype(np.uint64)
    x = x - ((x >> np.uint64(1)) & np.uint64(0x5555555555555555))
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return (x * np.uint64(0x0101010101010101)) >> np.uint64(56)


def parity(x: np.ndarray) -> np.ndarray:
    """Vectorized bit-parity (popcount mod 2), returned as int array."""
    return (popcount(x) % np.uint64(2)).astype(np.int64)


# ---------------------------------------------------------------------------
# Core gate-application routine
# ---------------------------------------------------------------------------


def apply_gate(state: np.ndarray, gate: np.ndarray, qubits: Sequence[int], n: int) -> np.ndarray:
    """Apply a ``2**k x 2**k`` gate matrix to the given ``qubits`` of an
    ``n``-qubit statevector ``state`` (length ``2**n``), returning the new
    statevector.

    ``qubits`` gives the axis order the gate matrix expects, e.g. for a
    controlled gate ``qubits = [control, target]``.
    """
    k = len(qubits)
    tensor = state.reshape((2,) * n)

    other_axes = [ax for ax in range(n) if ax not in qubits]
    perm = list(qubits) + other_axes
    tensor = np.transpose(tensor, perm)

    tensor = tensor.reshape(2 ** k, -1)
    tensor = gate @ tensor
    tensor = tensor.reshape((2,) * k + (2,) * (n - k))

    inv_perm = np.argsort(perm)
    tensor = np.transpose(tensor, inv_perm)
    return tensor.reshape(-1).astype(complex)


def zero_state(n: int) -> np.ndarray:
    """Return the ``|0...0>`` statevector for ``n`` qubits."""
    state = np.zeros(2 ** n, dtype=complex)
    state[0] = 1.0
    return state


def bitstring(index: int, n: int) -> str:
    """Render a basis-state index as an ``n``-bit binary string."""
    return format(index, f"0{n}b")


def probabilities(state: np.ndarray) -> np.ndarray:
    """Measurement probabilities for each computational basis state."""
    return np.abs(state) ** 2


def sample(state: np.ndarray, shots: int, rng: np.random.Generator | None = None) -> dict:
    """Sample ``shots`` projective measurements in the computational basis.

    Returns a dict mapping basis-state index -> observed count.
    """
    if rng is None:
        rng = np.random.default_rng()
    probs = probabilities(state)
    probs = probs / probs.sum()  # guard against tiny floating point drift
    outcomes = rng.choice(len(state), size=shots, p=probs)
    counts: dict = {}
    for outcome in outcomes:
        counts[int(outcome)] = counts.get(int(outcome), 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Fluent register wrapper used by the algorithm modules
# ---------------------------------------------------------------------------


class QuantumRegister:
    """A small fluent wrapper around a statevector plus the standard gate set.

    Every mutating method returns ``self`` so circuits can be built by
    chaining calls, e.g. ``QuantumRegister(3).h_all().cnot(0, 1)``.
    """

    def __init__(self, n_qubits: int, amplitudes: np.ndarray | None = None):
        self.n = n_qubits
        if amplitudes is None:
            self.amps = zero_state(n_qubits)
        else:
            amplitudes = np.asarray(amplitudes, dtype=complex)
            if amplitudes.shape != (2 ** n_qubits,):
                raise ValueError(
                    f"expected {2 ** n_qubits} amplitudes for {n_qubits} qubits, "
                    f"got shape {amplitudes.shape}"
                )
            norm = np.linalg.norm(amplitudes)
            if not np.isclose(norm, 1.0):
                raise ValueError(f"initial amplitudes must be normalized (||psi||={norm!r})")
            self.amps = amplitudes.copy()

    # -- single-qubit gates ------------------------------------------------

    def h(self, q: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, H, [q], self.n)
        return self

    def x(self, q: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, X, [q], self.n)
        return self

    def y(self, q: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, Y, [q], self.n)
        return self

    def z(self, q: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, Z, [q], self.n)
        return self

    def phase(self, q: int, theta: float) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, phase_gate(theta), [q], self.n)
        return self

    def h_all(self, qubits: Iterable[int] | None = None) -> "QuantumRegister":
        for q in (range(self.n) if qubits is None else qubits):
            self.h(q)
        return self

    # -- two-qubit gates -----------------------------------------------

    def cnot(self, control: int, target: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, CNOT, [control, target], self.n)
        return self

    def cz(self, control: int, target: int) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, CZ, [control, target], self.n)
        return self

    def cphase(self, control: int, target: int, theta: float) -> "QuantumRegister":
        self.amps = apply_gate(self.amps, controlled_phase(theta), [control, target], self.n)
        return self

    def swap(self, a: int, b: int) -> "QuantumRegister":
        if a == b:
            return self
        self.amps = apply_gate(self.amps, SWAP, [a, b], self.n)
        return self

    # -- oracle helper -------------------------------------------------

    def apply_diagonal_phase(self, phase_fn: Callable[[np.ndarray], np.ndarray]) -> "QuantumRegister":
        """Apply a diagonal unitary ``diag(phase_fn(0), ..., phase_fn(2^n-1))``.

        This is how every oracle in this package is implemented: a black-box
        function ``f`` marks basis states by multiplying their amplitude by
        ``phase_fn(x)`` (typically ``(-1) ** f(x)``, a unit-modulus phase).
        This is mathematically identical to the "phase kickback" oracle
        used in the textbook circuits (an ancilla qubit prepared in
        ``|-\\rangle`` that gets XORed with ``f(x)``), without needing to
        materialize the ancilla qubit or an exponentially large oracle
        matrix explicitly.
        """
        indices = np.arange(2 ** self.n)
        phases = np.asarray(phase_fn(indices))
        self.amps = self.amps * phases
        return self

    # -- measurement -----------------------------------------------------

    def probabilities(self) -> np.ndarray:
        return probabilities(self.amps)

    def most_probable(self) -> int:
        return int(np.argmax(self.probabilities()))

    def most_probable_bitstring(self) -> str:
        return bitstring(self.most_probable(), self.n)

    def sample(self, shots: int, rng: np.random.Generator | None = None) -> dict:
        return sample(self.amps, shots, rng)

    def copy(self) -> "QuantumRegister":
        clone = QuantumRegister.__new__(QuantumRegister)
        clone.n = self.n
        clone.amps = self.amps.copy()
        return clone

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"QuantumRegister(n={self.n})"
