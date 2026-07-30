# Quantum Algorithm Toolkit

A small, dependency-light Python library and CLI implementing four
canonical quantum algorithms on top of a **from-scratch numpy statevector
simulator** -- no Qiskit, Cirq, or other quantum SDK required for the core
library or test suite. Correctness of every algorithm is checked in
`pytest` against the known classical/theoretical answer.

Built as a teaching-quality reference: the linear algebra behind each
algorithm is implemented directly and kept readable, rather than hidden
behind a framework.

## Why numpy instead of a quantum SDK

Quantum SDKs like Qiskit are excellent for real hardware and large-scale
research, but they are heavy dependencies with slow install times, which
makes them a poor fit for a small, fast-to-test reference project. A
statevector is just a complex vector of length `2^n`, and gates are just
small matrices -- both are things numpy already does well. Implementing
the simulator directly:

- keeps `pip install` and CI to a few seconds (`numpy` + `pytest` only),
- makes the exact unitary behind every gate and oracle inspectable,
- and is enough to run every algorithm here at the qubit counts where
  they're useful for learning and demonstration.

An optional, thin Qiskit adapter (`quantum_toolkit/qiskit_adapter.py`) is
included to show how the same circuits could be expressed for a real
backend. It is **not** imported by anything else in the package and is
only needed if you explicitly install the `qiskit` extra.

## Scaling limits (read this before you set `--qubits 30`)

This is a **statevector simulator**: it stores every one of the `2^n`
complex amplitudes explicitly and applies gates as dense matrix
contractions. That means:

- Memory scales as `O(2^n)` and time per gate as `O(2^n)` (with an
  additional per-gate factor for multi-qubit gates and the QFT's
  `O(n^2)` gate count).
- On a typical laptop this is comfortable up to roughly 20-24 qubits and
  gets prohibitively slow/large well before 30.
- This is fundamentally how *all* classical statevector simulation works
  (it's precisely the exponential blowup that makes quantum computers
  interesting) -- it is not a limitation specific to this project.

In short: this toolkit is for **learning, demonstration, and correctness
testing of algorithms at small qubit counts**, not for simulating
production-scale quantum workloads. For that you'd want a real quantum
backend or a specialized large-scale simulator.

## Install

```bash
git clone https://github.com/Darviq-Systems/Quantum-Algorithm-Toolkit.git
cd Quantum-Algorithm-Toolkit
pip install -e ".[dev]"
```

Core runtime dependency: `numpy`. Dev/test dependency: `pytest`. Nothing
else is required.

## Run the tests

```bash
python -m pytest -v
```

All tests verify each algorithm against a known classical or theoretical
answer (exact recovered secrets, exact DFT cross-checks, Grover success
probabilities, etc.) across multiple qubit counts and random parameter
choices.

## CLI usage

```bash
# Grover's search: find a marked 4-bit item among 16
python -m quantum_toolkit grover --qubits 4 --marked 1011

# Deutsch-Jozsa: distinguish a constant vs. balanced oracle in one query
python -m quantum_toolkit dj --qubits 5 --oracle balanced --secret 22
python -m quantum_toolkit dj --qubits 5 --oracle constant --value 1

# Bernstein-Vazirani: recover a hidden bitstring in one query
python -m quantum_toolkit bv --qubits 6 --secret 101101

# Quantum Fourier Transform demo, cross-checked against numpy.fft
python -m quantum_toolkit qft --qubits 3 --seed 1
```

Example output (Grover):

```
Grover's search over 16 items (4 qubits)
  marked item        : 1011
  iterations used    : 3 (theoretical optimum: 3)
  measured result    : 1011
  P(measure marked)  : 0.9613
  success            : True
```

## The algorithms

### 1. Deutsch-Jozsa

**Problem:** given oracle access to `f: {0,1}^n -> {0,1}` promised to be
either *constant* (same output for every input) or *balanced* (0 on
exactly half the inputs, 1 on the other half), decide which.

**Why it's faster than classical:** a deterministic classical algorithm
needs up to `2^(n-1) + 1` queries in the worst case. Deutsch-Jozsa solves
it with a **single** quantum query -- an exponential separation.

```
|0>^n --- H^n ---[ Oracle: x -> (-1)^f(x) ]--- H^n --- measure
         superposition      phase kickback      interference
```

If `f` is constant, the two Hadamard layers cancel and you measure
`|0...0>` with certainty. If `f` is balanced, interference guarantees you
can *never* measure `|0...0>` -- so a single non-zero measurement proves
"balanced."

Module: `quantum_toolkit/algorithms/deutsch_jozsa.py`.

### 2. Grover's search

**Problem:** find a single marked item among `N = 2^n` unstructured
items, given oracle access that recognizes the marked item.

**Why it's faster than classical:** unstructured search classically
needs `O(N)` queries on average -- there's no structure to exploit.
Grover's algorithm finds the marked item with high probability using
only `O(sqrt(N))` queries, a proven quadratic speedup (and it's also
proven to be *optimal* -- no quantum algorithm can do better for
unstructured search).

```
|0>^n --- H^n ---[ Oracle: flip sign of |marked> ]---[ Diffusion ]--- ... ~pi/4*sqrt(N) times ... --- measure

Diffusion = H^n . (2|0><0| - I) . H^n   (reflection about the mean amplitude)
```

Each iteration is one oracle reflection plus one diffusion reflection,
which together rotate the statevector towards the marked state by a
fixed angle. Repeating this close to `pi/4 * sqrt(N)` times maximizes the
probability of measuring the marked item. The test suite checks both that
the marked item is found with high probability *and* that the number of
iterations used matches the theoretical optimum.

Module: `quantum_toolkit/algorithms/grover.py`.

### 3. Quantum Fourier Transform (QFT)

**Problem:** compute the discrete Fourier transform of the amplitudes of
a quantum register, `X_k = (1/sqrt(N)) * sum_j x_j * exp(2*pi*i*j*k/N)`.

**Why it's faster than classical:** the classical FFT computes a
length-`N` DFT in `O(N log N)` time. The QFT computes the same linear
transform on an `n`-qubit register's amplitudes using only `O(n^2)`
gates -- exponentially fewer gates than the classical FFT needs
operations (the catch: you can't read out all `N` transformed amplitudes
directly, since measurement collapses the state to just one basis
outcome). The QFT is the key subroutine behind Shor's algorithm and
quantum phase estimation.

```
q0: --H--o--------o----------------x---
          |        |                |
q1: -----P(pi/2)--|----H--o---------|---
                   |       |         |
q2: ---------------P(pi/4)-P(pi/2)--H--x---   (then swap q0 <-> q2)
```

(Three-qubit example: each qubit gets a Hadamard followed by
controlled-phase rotations from every qubit below it, with angles
halving each step, then a final swap layer reverses qubit order.)

The test suite verifies the circuit output against `sqrt(N) *
numpy.fft.ifft(...)` computed directly on the same input amplitudes --
i.e. an independent classical reference implementation, not just an
internal self-consistency check.

Module: `quantum_toolkit/algorithms/qft.py`.

### 4. Bernstein-Vazirani

**Problem:** given oracle access to `f(x) = x . s (mod 2)` for a hidden
`n`-bit secret string `s`, recover `s`.

**Why it's faster than classical:** classically this takes `n` queries
(probe each standard basis vector to peel off one bit of `s` at a time).
Bernstein-Vazirani recovers the *entire* secret string in a **single**
quantum query -- an `O(n)` -> `O(1)` separation in query complexity.

```
|0>^n --- H^n ---[ Oracle: x -> (-1)^(x.s) ]--- H^n --- measure --> s
```

Measuring the register after the second Hadamard layer yields the secret
string `s` directly and exactly, every time.

Module: `quantum_toolkit/algorithms/bernstein_vazirani.py`.

## Project layout

```
src/quantum_toolkit/
  simulator.py              # statevector core: gates, apply_gate, QuantumRegister
  cli.py, __main__.py       # `python -m quantum_toolkit ...`
  qiskit_adapter.py         # optional Qiskit bridge (extra, not used by core/tests)
  algorithms/
    deutsch_jozsa.py
    grover.py
    qft.py
    bernstein_vazirani.py
tests/                      # pytest suite, one file per algorithm + simulator core
.github/workflows/ci.yml    # installs numpy+pytest, runs the suite on push/PR
```

## How the simulator works

An `n`-qubit register is a complex vector of length `2^n`; basis state
index `i` is the computational basis ket where qubit 0 is the
most-significant bit of `i`. Gates are applied by reshaping the flat
statevector into an `n`-index tensor of shape `(2,) * n`, permuting the
target qubit axes to the front, contracting with the (small, dense) gate
matrix, and permuting back -- a single `apply_gate` routine handles
single-qubit gates, controlled gates, and any other small multi-qubit
gate without ever materializing an exponentially large operator for the
whole register. Oracles are implemented as diagonal phase gates
(`(-1)^f(x)` per basis state), which is the standard "phase kickback"
simplification of the textbook ancilla-qubit oracle construction.

## License

MIT
