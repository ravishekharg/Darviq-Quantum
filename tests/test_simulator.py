import numpy as np
import pytest

from quantum_toolkit.simulator import (
    QuantumRegister,
    apply_gate,
    bitstring,
    parity,
    popcount,
    probabilities,
    zero_state,
)


def test_zero_state():
    state = zero_state(3)
    assert state.shape == (8,)
    assert state[0] == 1.0
    assert np.allclose(state[1:], 0.0)


def test_hadamard_creates_uniform_superposition():
    reg = QuantumRegister(3).h_all()
    probs = reg.probabilities()
    assert np.allclose(probs, np.full(8, 1 / 8))
    assert np.isclose(probs.sum(), 1.0)


def test_x_gate_flips_bit():
    reg = QuantumRegister(3)
    reg.x(0)
    # qubit 0 is the most-significant bit -> index 100b = 4
    assert reg.most_probable() == 0b100


def test_double_x_is_identity():
    reg = QuantumRegister(2)
    reg.x(1).x(1)
    assert np.isclose(reg.probabilities()[0], 1.0)


def test_cnot_creates_bell_state():
    reg = QuantumRegister(2)
    reg.h(0).cnot(0, 1)
    probs = reg.probabilities()
    # Bell state: equal superposition of |00> and |11> only.
    assert np.isclose(probs[0b00], 0.5)
    assert np.isclose(probs[0b11], 0.5)
    assert np.isclose(probs[0b01], 0.0)
    assert np.isclose(probs[0b10], 0.0)


def test_swap_gate():
    reg = QuantumRegister(2)
    reg.x(0)  # |10>
    assert reg.most_probable() == 0b10
    reg.swap(0, 1)
    assert reg.most_probable() == 0b01


def test_probabilities_always_normalized_after_gates():
    rng = np.random.default_rng(0)
    for n in (1, 2, 3, 4, 5):
        reg = QuantumRegister(n)
        for _ in range(10):
            q = int(rng.integers(0, n))
            gate_choice = rng.integers(0, 3)
            if gate_choice == 0:
                reg.h(q)
            elif gate_choice == 1:
                reg.x(q)
            else:
                reg.phase(q, float(rng.uniform(0, 2 * np.pi)))
        assert np.isclose(reg.probabilities().sum(), 1.0, atol=1e-9)


def test_apply_gate_matches_manual_kron_for_two_qubits():
    # Cross-check apply_gate against an explicit 4x4 Kronecker-product
    # construction for a simple two-qubit case (H on qubit 0, I on qubit 1).
    H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    I2 = np.eye(2, dtype=complex)
    full_gate = np.kron(H, I2)

    state = zero_state(2)
    state[2] = 1.0  # start from |10>, renormalize
    state = state / np.linalg.norm(state)

    via_apply_gate = apply_gate(state, H, [0], 2)
    via_manual = full_gate @ state
    assert np.allclose(via_apply_gate, via_manual)


def test_bitstring_formatting():
    assert bitstring(0, 4) == "0000"
    assert bitstring(5, 4) == "0101"
    assert bitstring(15, 4) == "1111"


def test_popcount_and_parity():
    values = np.array([0, 1, 2, 3, 7, 255], dtype=np.int64)
    expected_popcount = np.array([bin(v).count("1") for v in values])
    assert np.array_equal(popcount(values), expected_popcount)
    assert np.array_equal(parity(values), expected_popcount % 2)


def test_register_rejects_non_normalized_input():
    with pytest.raises(ValueError):
        QuantumRegister(2, np.array([1, 1, 0, 0], dtype=complex))


def test_register_rejects_wrong_length():
    with pytest.raises(ValueError):
        QuantumRegister(2, np.array([1, 0, 0], dtype=complex))
