import numpy as np
import pytest

from quantum_toolkit.algorithms.qft import classical_dft_reference, qft


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_qft_matches_classical_dft_on_random_states(n):
    rng = np.random.default_rng(100 + n)
    N = 2 ** n
    for _ in range(5):
        amplitudes = rng.normal(size=N) + 1j * rng.normal(size=N)
        amplitudes = amplitudes / np.linalg.norm(amplitudes)

        output = qft(amplitudes)
        reference = classical_dft_reference(amplitudes)

        assert np.allclose(output, reference, atol=1e-9)
        # Unitary: output must remain normalized.
        assert np.isclose(np.linalg.norm(output), 1.0, atol=1e-9)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_qft_on_basis_states_matches_dft(n):
    N = 2 ** n
    for basis_index in range(N):
        amplitudes = np.zeros(N, dtype=complex)
        amplitudes[basis_index] = 1.0

        output = qft(amplitudes)
        reference = classical_dft_reference(amplitudes)
        assert np.allclose(output, reference, atol=1e-9)


def test_qft_of_zero_state_is_uniform_superposition():
    n = 4
    amplitudes = np.zeros(2 ** n, dtype=complex)
    amplitudes[0] = 1.0
    output = qft(amplitudes)
    assert np.allclose(np.abs(output), 1 / np.sqrt(2 ** n), atol=1e-9)


def test_qft_is_its_own_kind_of_unitary_roundtrip():
    # Applying QFT then its classical inverse (fft, undoing the sqrt(N)*ifft)
    # should return (approximately) the original amplitudes.
    n = 5
    rng = np.random.default_rng(5)
    N = 2 ** n
    amplitudes = rng.normal(size=N) + 1j * rng.normal(size=N)
    amplitudes = amplitudes / np.linalg.norm(amplitudes)

    transformed = qft(amplitudes)
    # Undo: amplitudes = (1/sqrt(N)) * fft(transformed)
    recovered = (1.0 / np.sqrt(N)) * np.fft.fft(transformed)
    assert np.allclose(recovered, amplitudes, atol=1e-9)
