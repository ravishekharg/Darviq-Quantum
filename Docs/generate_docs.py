"""Generates the Darviq Quantum HLD and LLD .docx documents.

Run from anywhere with:  python Docs/generate_docs.py

Depends on docx_builder.py (copied into this Docs/ folder) and python-docx.
Regenerate this file's output any time the repo's structure/algorithms change
materially; it is kept in Docs/ for that purpose (not required at runtime by
the quantum_toolkit package itself).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_builder import DesignDoc

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.0"
DATE = "July 31, 2026"
PROJECT = "Darviq Quantum"
SUBTITLE = "Numpy Statevector Quantum Algorithm Simulator & CLI"


# ===========================================================================
# HLD
# ===========================================================================

def build_hld() -> DesignDoc:
    doc = DesignDoc(
        project_name=PROJECT,
        subtitle=SUBTITLE,
        doc_kind="High-Level Design (HLD)",
        version=VERSION,
        date=DATE,
    )
    doc.add_document_control()
    doc.add_toc_field()

    # 1. Introduction
    doc.add_heading1("1. Introduction")
    doc.add_heading2("1.1 Purpose")
    doc.add_paragraph(
        "This document describes the high-level design of Darviq Quantum "
        "(package name quantum_toolkit), a small, dependency-light Python "
        "library and command-line tool that implements four canonical "
        "quantum algorithms -- Deutsch-Jozsa, Grover's search, the Quantum "
        "Fourier Transform (QFT), and Bernstein-Vazirani -- on top of a "
        "from-scratch numpy statevector simulator. It explains why the "
        "project is built on plain numpy rather than a full quantum SDK, "
        "how its components fit together, and the constraints that follow "
        "from being a statevector simulator rather than a real quantum "
        "backend."
    )
    doc.add_heading2("1.2 Scope")
    doc.add_paragraph("In scope for this document:")
    doc.add_bullets([
        "The statevector simulator core (gate application, qubit register abstraction).",
        "The four implemented algorithm modules and their circuit structure.",
        "The CLI that exposes each algorithm as a runnable subcommand.",
        "The optional Qiskit adapter and its relationship to the core library.",
        "Packaging, testing, and non-functional characteristics (notably scaling limits).",
    ])
    doc.add_paragraph("Out of scope for this document:")
    doc.add_bullets([
        "Execution on real quantum hardware or any cloud quantum backend.",
        "Algorithms not currently implemented in the repository (e.g. Shor's algorithm, "
        "quantum phase estimation, VQE) -- these are noted only as possible future work.",
        "Detailed line-by-line code walkthrough (covered in the companion Low-Level Design document).",
    ])
    doc.add_heading2("1.3 Intended audience")
    doc.add_bullets([
        "Engineers or students evaluating or extending the toolkit.",
        "Reviewers assessing the project for a portfolio/teaching-quality reference.",
        "Contributors adding new algorithms or gates to the simulator.",
    ])
    doc.add_heading2("1.4 Definitions & abbreviations")
    doc.add_table(
        headers=["Term", "Definition"],
        rows=[
            ["Qubit", "The quantum analogue of a classical bit; an abstract two-level system whose state is a complex linear combination of |0> and |1>."],
            ["Statevector", "The complete quantum state of an n-qubit register, represented as a complex vector of 2^n amplitudes, one per computational basis state."],
            ["Gate", "A unitary operation (represented here as a small complex matrix, e.g. 2x2 for one qubit or 4x4 for two) applied to one or more qubits."],
            ["Superposition", "A quantum state that is a linear combination of more than one basis state simultaneously, e.g. equal superposition of |0> and |1> after a Hadamard gate."],
            ["Amplitude", "A complex number attached to a basis state in the statevector; its squared magnitude gives the probability of measuring that basis state."],
            ["Measurement", "The act of sampling a basis state from the statevector with probability equal to the squared magnitude of its amplitude, collapsing the state."],
            ["Oracle", "A black-box function f embedded into the circuit as a unitary (here, a diagonal phase gate) that the algorithm queries without inspecting its internals directly."],
            ["Phase kickback", "A standard simplification where an oracle's effect on an ancilla qubit is expressed instead as a phase (-1)^f(x) applied directly to the data register."],
            ["Diffusion operator", "The Grover-specific unitary 2|s><s| - I that reflects the statevector about the mean amplitude, used for amplitude amplification."],
            ["QFT", "Quantum Fourier Transform -- the quantum circuit analogue of the discrete Fourier transform (DFT), implemented with Hadamards and controlled-phase rotations."],
            ["Bell state", "A maximally entangled two-qubit state, e.g. (|00> + |11>)/sqrt(2), produced here by a Hadamard followed by a CNOT."],
            ["CLI", "Command-Line Interface -- here, the `python -m quantum_toolkit <command>` entry point."],
        ],
    )

    # 2. System overview
    doc.add_heading1("2. System overview")
    doc.add_heading2("2.1 Problem statement")
    doc.add_paragraph(
        "Learning quantum algorithms is usually done either through pure "
        "pen-and-paper linear algebra, or through a full quantum SDK "
        "(Qiskit, Cirq, etc.) whose abstractions and heavy dependency "
        "footprint can obscure the underlying mathematics. Darviq Quantum "
        "exists to close that gap: it lets a learner or engineer run and "
        "inspect the exact statevector transformations behind four "
        "textbook algorithms that demonstrate real, proven quantum "
        "speedups over the best possible classical algorithm -- "
        "Deutsch-Jozsa (exponential query separation), Grover's search "
        "(proven-optimal quadratic speedup), the QFT (the core subroutine "
        "behind Shor's algorithm and phase estimation), and "
        "Bernstein-Vazirani (an O(n) -> O(1) query separation) -- with "
        "every gate, oracle, and measurement result correctness-checked "
        "against a known classical or theoretical answer in the test suite."
    )
    doc.add_heading2("2.2 Proposed solution summary")
    doc.add_paragraph(
        "The toolkit implements its own minimal statevector simulator "
        "directly on top of numpy rather than depending on a quantum SDK. "
        "An n-qubit register is stored as a complex numpy array of length "
        "2^n; gates are small dense matrices (2x2 for single-qubit gates, "
        "4x4 for two-qubit gates); and a single generic apply_gate routine "
        "applies any such gate to any subset of qubits by reshaping the "
        "flat statevector into an n-axis tensor, permuting the target "
        "qubit axes to the front, contracting with the gate matrix, and "
        "permuting back -- without ever materializing an exponentially "
        "large operator for the whole register. This keeps the runtime "
        "dependency surface to numpy alone (pytest for the dev/test extra), "
        "keeps install and CI times to a few seconds, and keeps the exact "
        "unitary behind every gate and oracle directly inspectable in "
        "readable Python. A thin, optional Qiskit adapter is included "
        "purely for illustration of how the same circuits map onto a real "
        "SDK/backend; it is not imported by, or required for, any core "
        "functionality."
    )

    # 3. Architecture overview
    doc.add_heading1("3. Architecture overview")
    doc.add_table(
        headers=["Component", "Responsibility", "Technology"],
        rows=[
            ["Statevector simulator core (simulator.py)", "Gate matrix definitions, generic apply_gate tensor-contraction routine, QuantumRegister fluent wrapper, measurement/sampling utilities, bit-parity helpers", "numpy"],
            ["Gate library (module-level constants/functions in simulator.py)", "Standard gate matrices: H, X, Y, Z, phase_gate(theta), CNOT, CZ, SWAP, controlled_phase(theta)", "numpy"],
            ["Deutsch-Jozsa module (algorithms/deutsch_jozsa.py)", "Constant/balanced oracle constructors and the single-query constant-vs-balanced circuit + verdict logic", "numpy, simulator core"],
            ["Grover module (algorithms/grover.py)", "Optimal iteration-count formula, oracle phase flip, diffusion operator, full search loop", "numpy (math for iteration count), simulator core"],
            ["QFT module (algorithms/qft.py)", "Textbook QFT circuit construction (Hadamard + controlled-phase ladder + swap layer) and a classical DFT cross-check reference", "numpy, simulator core"],
            ["Bernstein-Vazirani module (algorithms/bernstein_vazirani.py)", "Single-query hidden-string recovery circuit", "numpy, simulator core"],
            ["CLI (cli.py, __main__.py)", "argparse-based subcommands (grover, dj, bv, qft) that parse arguments, invoke the corresponding algorithm module, and print human-readable results", "argparse, Python standard library"],
            ["Qiskit adapter (qiskit_adapter.py, optional)", "Illustrative re-expression of the Bernstein-Vazirani and Grover circuits using explicit ancilla qubits and Qiskit's QuantumCircuit API", "qiskit (optional extra only)"],
            ["Test suite (tests/)", "Pytest coverage validating every algorithm and the simulator core against known classical/theoretical answers", "pytest"],
            ["CI pipeline (.github/workflows/ci.yml)", "Installs the dev extra, runs the test suite, and smoke-tests all four CLI subcommands on Python 3.9/3.11/3.12", "GitHub Actions"],
        ],
    )
    doc.add_heading2("3.1 Component descriptions")
    doc.add_paragraph(
        "The simulator core is the single foundation every algorithm module "
        "is built on. It exposes a QuantumRegister class that wraps a "
        "statevector array together with chainable single- and two-qubit "
        "gate methods (h, x, y, z, phase, h_all, cnot, cz, cphase, swap) "
        "and an apply_diagonal_phase helper used by every oracle in the "
        "package. Each algorithm module is a small, self-contained file "
        "that builds a QuantumRegister, applies a specific gate sequence, "
        "and interprets the resulting probabilities or most-probable basis "
        "state. The CLI is a thin argparse wrapper with one subcommand per "
        "algorithm; it performs input validation (bitstring length/alphabet "
        "checks) before delegating to the algorithm module and formats the "
        "returned results for the terminal. The Qiskit adapter is "
        "architecturally isolated -- nothing in the core package or test "
        "suite imports it -- so the mandatory dependency footprint stays "
        "at numpy alone."
    )

    # 4. End-to-end functional workflow
    doc.add_heading1("4. End-to-end functional workflow")
    doc.add_figure_placeholder(
        "Figure 1: CLI invocation -> argument validation -> circuit construction "
        "-> statevector simulation -> measurement/verdict -> formatted stdout output"
    )
    doc.add_paragraph(
        "A user invokes one of the four subcommands via "
        "`python -m quantum_toolkit <grover|dj|bv|qft> [options]`. "
        "__main__.py delegates to cli.main(), which builds an argparse "
        "parser (build_parser()) and dispatches to the matching "
        "_cmd_<name> function. Each _cmd_ function first validates its "
        "arguments (e.g. that --marked or --secret is a binary string of "
        "exactly the requested qubit length), then calls the corresponding "
        "algorithm module's run_* function, which constructs a "
        "QuantumRegister, applies the algorithm's fixed gate sequence "
        "(superposition via Hadamards, an oracle as a diagonal phase gate, "
        "further gates specific to the algorithm, and for Grover a repeated "
        "oracle+diffusion loop), and returns either the most probable "
        "measured bitstring, a verdict string (\"constant\"/\"balanced\"), "
        "or, for QFT, the transformed amplitude vector plus a classical "
        "DFT reference for comparison. The _cmd_ function then formats the "
        "result -- including iteration counts, probabilities, and a "
        "success/verdict line -- and prints it to stdout, returning a "
        "process exit code (0 on success, 1 on validation failure)."
    )

    # 5. Module-wise design overview
    doc.add_heading1("5. Module-wise design overview")

    doc.add_heading2("5.1 Simulator core (simulator.py)")
    doc.add_paragraph(
        "Defines the gate matrices (I2, H, X, Y, Z, phase_gate, CNOT, CZ, "
        "SWAP, controlled_phase), the vectorized popcount/parity bit "
        "utilities used to build oracle phase functions, the generic "
        "apply_gate(state, gate, qubits, n) tensor-contraction routine "
        "that every gate call ultimately runs through, and the "
        "QuantumRegister fluent class that wraps a statevector together "
        "with chainable gate methods, an apply_diagonal_phase oracle "
        "helper, and measurement/sampling methods (probabilities, "
        "most_probable, most_probable_bitstring, sample)."
    )

    doc.add_heading2("5.2 Deutsch-Jozsa (algorithms/deutsch_jozsa.py)")
    doc.add_paragraph(
        "Purpose: given oracle access to f: {0,1}^n -> {0,1} promised to be "
        "either constant or balanced, decide which in a single query -- an "
        "exponential separation from the up-to-2^(n-1)+1 queries a "
        "deterministic classical algorithm needs in the worst case. Circuit "
        "structure: H^n (uniform superposition) -> oracle as a diagonal "
        "phase (-1)^f(x) -> H^n again -> measure. If f is constant the two "
        "Hadamard layers cancel and |0...0> is measured with certainty; if "
        "f is balanced, interference guarantees the |0...0> amplitude is "
        "exactly zero, so any non-zero measurement certifies \"balanced\". "
        "The module provides constant_oracle(value) and "
        "balanced_oracle(secret) as oracle constructors, and "
        "run_deutsch_jozsa(n, oracle_fn) to run the full circuit and return "
        "the verdict plus the full probability vector."
    )

    doc.add_heading2("5.3 Grover's search (algorithms/grover.py)")
    doc.add_paragraph(
        "Purpose: find one marked item among N = 2^n unstructured items, "
        "given oracle access that recognizes it -- a proven-optimal "
        "quadratic speedup (O(sqrt(N)) queries) over the O(N) a classical "
        "linear scan needs. Circuit structure: H^n to build the uniform "
        "superposition, then a fixed number of iterations of (oracle phase "
        "flip on the marked basis state) followed by (diffusion operator "
        "H^n . (2|0><0| - I) . H^n, i.e. reflect about the mean amplitude), "
        "then measure. The module computes the iteration count with "
        "optimal_iterations(n), which uses the exact geometric rotation "
        "angle rather than the naive pi/4*sqrt(N) rounding (the two can "
        "disagree by one iteration at small N and the exact formula avoids "
        "overshooting). grover_search(n, marked, iterations) runs the raw "
        "circuit and run_grover(n, marked_bitstring, iterations) is the "
        "bitstring-based convenience wrapper used by the CLI."
    )

    doc.add_heading2("5.4 Quantum Fourier Transform (algorithms/qft.py)")
    doc.add_paragraph(
        "Purpose: compute the discrete Fourier transform of an n-qubit "
        "register's amplitudes using only O(n^2) gates -- exponentially "
        "fewer gates than the O(N log N) operations the classical FFT "
        "needs for the same size N=2^n input (with the caveat that "
        "measurement can only ever read out one collapsed basis state, "
        "not all N transformed amplitudes at once). It is the key "
        "subroutine behind Shor's algorithm and quantum phase estimation. "
        "Circuit structure (apply_qft): for each qubit j from 0 to n-1, "
        "apply a Hadamard, then a controlled-phase rotation from every "
        "qubit k below it with angle pi/2^(k-j), then (by default) a final "
        "layer of swaps reversing the qubit order to match the standard "
        "output convention. The module also provides "
        "classical_dft_reference(amplitudes), an independent numpy.fft-based "
        "reference (sqrt(N) * numpy.fft.ifft(amplitudes)) used by the test "
        "suite and the CLI's own cross-check output to verify correctness "
        "against a source outside the simulator itself."
    )

    doc.add_heading2("5.5 Bernstein-Vazirani (algorithms/bernstein_vazirani.py)")
    doc.add_paragraph(
        "Purpose: given oracle access to f(x) = x . s (mod 2) for a hidden "
        "n-bit secret s, recover s entirely -- an O(n) -> O(1) query "
        "separation versus the n classical queries needed to peel off one "
        "bit of s at a time. Circuit structure: H^n -> oracle as diagonal "
        "phase (-1)^(x.s) -> H^n -> measure; the secret s is recovered "
        "exactly (probability 1) as the most-probable basis state, no "
        "repetition needed. run_bernstein_vazirani(n, secret) implements "
        "this directly, reusing the same parity() bit-utility that backs "
        "Deutsch-Jozsa's balanced_oracle (the two oracle families are the "
        "same function shape)."
    )

    # 6. Data design
    doc.add_heading1("6. Data design: core data structures")
    doc.add_bullets([
        "Statevector: a 1-D numpy complex array of length 2^n; index i is the computational basis ket where bit 0 of i (the register's qubit 0) is the most-significant bit, consistent across every gate, oracle, and algorithm.",
        "Gate matrix: a small dense complex numpy array (2x2 for single-qubit gates such as H, X, Y, Z, phase_gate(theta); 4x4 for two-qubit gates such as CNOT, CZ, SWAP, controlled_phase(theta)), applied via the generic apply_gate tensor-reshape-and-contract routine rather than an exponentially large full-register operator.",
        "QuantumRegister: the fluent wrapper class holding .n (qubit count) and .amps (the statevector), with chainable gate methods, an apply_diagonal_phase oracle helper, and measurement methods (probabilities, most_probable, most_probable_bitstring, sample, copy). Validates on construction that any supplied initial amplitude vector has the correct length (2^n) and is normalized.",
        "Oracle phase function: a vectorized callable indices -> phases mapping each basis-state index to a unit-modulus complex phase (typically (-1)**f(x)); this is the diagonal-matrix simplification of the textbook ancilla-qubit oracle used by every algorithm in the package.",
    ])

    # 7. Technology stack
    doc.add_heading1("7. Technology stack")
    doc.add_table(
        headers=["Layer", "Technology", "Notes"],
        rows=[
            ["Language / runtime", "Python >= 3.9", "CI matrix tests 3.9, 3.11, and 3.12"],
            ["Numerical core", "numpy >= 1.24", "Sole mandatory runtime dependency; statevector storage and gate contraction"],
            ["CLI", "argparse (standard library)", "No third-party CLI framework"],
            ["Testing", "pytest >= 7.4 (dev extra)", "Correctness checks against known classical/theoretical answers"],
            ["Packaging", "setuptools >= 68 / wheel", "src/ layout, package discovered under src/quantum_toolkit"],
            ["Optional SDK bridge", "qiskit >= 1.0 (qiskit extra)", "Illustrative only; not imported by core package or tests"],
            ["CI", "GitHub Actions (.github/workflows/ci.yml)", "Runs test suite + CLI smoke tests on push/PR to main"],
        ],
    )

    # 8. Deployment architecture -> packaging & execution model
    doc.add_heading1("8. Packaging & execution model")
    doc.add_paragraph(
        "There is no server or hosted deployment for this project -- it is "
        "a locally installed library and CLI. It is installed with "
        "`pip install -e \".[dev]\"` from a clone (src/ layout package "
        "named quantum_toolkit, distribution name quantum-toolkit, "
        "declared in pyproject.toml), which also registers a "
        "`quantum-toolkit` console-script entry point in addition to the "
        "`python -m quantum_toolkit` module-execution form. Running the "
        "test suite is `python -m pytest -v`. Because the only mandatory "
        "dependency is numpy, both install and the full test suite "
        "complete in a few seconds, which is deliberate: it keeps the "
        "project fast to clone, install, and verify for a reader who just "
        "wants to see the algorithms run. The optional Qiskit extra "
        "(`pip install .[qiskit]`) is only needed to use "
        "qiskit_adapter.py; it is never installed or exercised by CI."
    )

    # 9. Security design
    doc.add_heading1("9. Security design")
    doc.add_paragraph(
        "This is a local, offline command-line simulation library with no "
        "network listeners, no persisted user data, no authentication "
        "surface, and no external service calls -- it reads CLI arguments "
        "and numpy-generated random numbers, computes in memory, and "
        "prints to stdout. There is genuinely no security-relevant design "
        "to document beyond standard supply-chain hygiene (pinning numpy "
        ">= 1.24 and pytest >= 7.4 as the only dependencies, and keeping "
        "the optional qiskit extra strictly opt-in and unimported by "
        "default). Input validation in the CLI (bitstring length and "
        "alphabet checks) exists for correctness rather than as a security "
        "control."
    )

    # 10. Non-functional requirements
    doc.add_heading1("10. Non-functional requirements")
    doc.add_table(
        headers=["Attribute", "Target / approach"],
        rows=[
            ["Statevector memory scaling", "O(2^n) complex128 amplitudes -- 16 bytes/amplitude, e.g. ~16 MB at n=20, ~16 GB at n=30"],
            ["Per-gate time scaling", "O(2^n) per single/two-qubit gate application (tensor reshape + small-matrix contraction); QFT additionally applies O(n^2) gates in total"],
            ["Practical qubit-count ceiling", "Comfortable up to roughly 20-24 qubits on a typical laptop; prohibitively slow/large well before 30, per the README's own guidance"],
            ["Numerical precision", "complex128 (numpy default complex dtype) throughout; probabilities renormalized defensively before sampling to absorb floating-point drift"],
            ["Install / CI time", "A few seconds end-to-end, since numpy + pytest are the only dependencies exercised by CI"],
            ["Correctness verification", "Every algorithm cross-checked in pytest against an independent classical/theoretical answer (exact recovered secrets, exact DFT via numpy.fft, Grover success probability and theoretical-optimum iteration count) across multiple qubit counts and randomized parameters"],
            ["Portability", "Pure Python + numpy; no OS-specific or hardware-specific code; runs anywhere numpy runs"],
        ],
    )

    # 11. Assumptions & constraints
    doc.add_heading1("11. Assumptions & constraints")
    doc.add_bullets([
        "This is a statevector simulator, not a real quantum backend: it stores every one of the 2^n complex amplitudes explicitly, so its exponential memory/time scaling is fundamental to classical simulation of quantum systems, not an implementation shortcoming.",
        "No real quantum hardware backend is targeted or supported by the core library; the optional Qiskit adapter only illustrates how the same circuits could be re-expressed for a real backend/transpiler, it does not execute on one.",
        "The toolkit is scoped to small, teaching-scale qubit counts (roughly up to 20-24 qubits) where learning, demonstration, and automated correctness-checking are the goals -- not production-scale quantum workload simulation.",
        "Each algorithm assumes noiseless, ideal unitary evolution (no decoherence or gate-error modeling), matching the textbook circuits being demonstrated.",
        "Oracles are implemented via the phase-kickback simplification (a diagonal phase gate on the data qubits) rather than an explicit ancilla qubit; this is mathematically equivalent to, but structurally simpler than, the textbook ancilla-based oracle circuit.",
    ])

    # 12. Future enhancements
    doc.add_heading1("12. Future enhancements")
    doc.add_bullets([
        "Expand the illustrative Qiskit adapter to cover Deutsch-Jozsa and QFT circuits as well (currently only Bernstein-Vazirani and Grover are mirrored there).",
        "Add further canonical algorithms building on the existing QFT subroutine, most naturally quantum phase estimation and Shor's factoring algorithm, both explicitly named in the QFT module's own docstring as the algorithms it underpins.",
        "Add a noise/error-model option (e.g. depolarizing or measurement noise) for readers who want to see how these algorithms degrade outside the ideal-unitary assumption.",
        "Add a lightweight circuit-diagram renderer so users can visualize the gate sequence for a given CLI invocation instead of only reading the ASCII diagrams in the README.",
    ])

    # 13. Appendix
    doc.add_heading1("13. Appendix")
    doc.add_heading2("13.1 References")
    doc.add_bullets([
        "Repository README.md (algorithm descriptions, scaling-limit guidance, CLI usage examples)",
        "Nielsen & Chuang, Quantum Computation and Quantum Information (standard reference for Deutsch-Jozsa, Grover, QFT, and Bernstein-Vazirani circuit constructions)",
        "src/quantum_toolkit/simulator.py, algorithms/*.py, cli.py (source of truth for all behavior described in this document)",
        "Companion document: Darviq_Quantum_Low_Level_Design.docx",
    ])
    doc.add_heading2("13.2 Change history")
    doc.add_table(
        headers=["Version", "Date", "Description"],
        rows=[["1.0", DATE, "Initial high-level design document"]],
    )

    return doc


# ===========================================================================
# LLD
# ===========================================================================

def build_lld() -> DesignDoc:
    doc = DesignDoc(
        project_name=PROJECT,
        subtitle=SUBTITLE,
        doc_kind="Low-Level Design (LLD)",
        version=VERSION,
        date=DATE,
    )
    doc.add_document_control()
    doc.add_toc_field()

    # 1. Introduction
    doc.add_heading1("1. Introduction")
    doc.add_heading2("1.1 Purpose")
    doc.add_paragraph(
        "This document provides the low-level design for Darviq Quantum, "
        "detailing the concrete implementation of the simulator core, each "
        "algorithm module, the CLI, and the data structures/gate set "
        "described at a high level in the companion HLD document "
        "(Darviq_Quantum_High_Level_Design.docx). It cites real file paths, "
        "real class/function/gate names, and the actual gate sequences and "
        "formulas implemented in the repository."
    )
    doc.add_heading2("1.2 Scope")
    doc.add_paragraph(
        "Covers: the QuantumRegister/statevector data structure and gate "
        "reference; the CLI command reference; step-by-step execution "
        "flows for each algorithm; the exact mathematical formulas used "
        "(Grover iteration count, QFT construction, Deutsch-Jozsa and "
        "Bernstein-Vazirani oracle/recovery logic); input validation and "
        "known gaps; and scaling/precision considerations. It does not "
        "repeat the architectural rationale already covered in the HLD."
    )
    doc.add_heading2("1.3 References")
    doc.add_bullets([
        "Darviq_Quantum_High_Level_Design.docx (companion HLD)",
        "src/quantum_toolkit/simulator.py",
        "src/quantum_toolkit/algorithms/deutsch_jozsa.py",
        "src/quantum_toolkit/algorithms/grover.py",
        "src/quantum_toolkit/algorithms/qft.py",
        "src/quantum_toolkit/algorithms/bernstein_vazirani.py",
        "src/quantum_toolkit/cli.py, src/quantum_toolkit/__main__.py",
        "src/quantum_toolkit/qiskit_adapter.py",
        "tests/test_simulator.py, tests/test_grover.py, tests/test_deutsch_jozsa.py, tests/test_qft.py, tests/test_bernstein_vazirani.py",
        "pyproject.toml, .github/workflows/ci.yml",
    ])

    # 2. Detailed module design
    doc.add_heading1("2. Detailed module design")

    doc.add_heading2("2.1 Deutsch-Jozsa -- src/quantum_toolkit/algorithms/deutsch_jozsa.py")
    doc.add_paragraph(
        "constant_oracle(value) returns a vectorized phase_fn(x) = "
        "full_like(x, -1 if value else 1) -- i.e. f(x)=value for every x. "
        "balanced_oracle(secret) (secret must be nonzero) returns "
        "phase_fn(x) = where(parity(x & secret) == 1, -1, 1), i.e. "
        "f(x) = parity(x AND secret), which is balanced for any nonzero "
        "secret and is the same function family used by Bernstein-Vazirani. "
        "run_deutsch_jozsa(n, oracle_fn) builds QuantumRegister(n), calls "
        "reg.h_all() (Hadamard on every qubit, building the uniform "
        "superposition), reg.apply_diagonal_phase(oracle_fn) (the oracle, "
        "applied as a diagonal phase multiply directly on reg.amps), then "
        "reg.h_all() again, and returns (verdict, probs) where verdict is "
        "\"constant\" if probs[0] is close to 1.0 (atol=1e-9) and "
        "\"balanced\" otherwise."
    )

    doc.add_heading2("2.2 Grover's search -- src/quantum_toolkit/algorithms/grover.py")
    doc.add_paragraph(
        "optimal_iterations(n) computes theta = 2*asin(1/sqrt(N)) (N=2^n) "
        "and returns max(1, round(pi/(2*theta) - 0.5)) -- the exact integer "
        "iteration count that maximizes overlap with the marked state "
        "(noted in the module docstring to sometimes differ by one from "
        "the naive asymptotic round(pi/4*sqrt(N)) estimate at small N). "
        "_diffusion(reg) implements the diffusion operator as reg.h_all(), "
        "then reg.amps[0] *= -1.0 (reflect about |0...0>), then reg.h_all() "
        "again -- the standard H^n . (2|0><0| - I) . H^n decomposition. "
        "grover_search(n, marked, iterations) builds QuantumRegister(n), "
        "calls reg.h_all(), validates 0 <= marked < 2**n, then for each "
        "iteration (default optimal_iterations(n) if not overridden) "
        "flips the sign of reg.amps[marked] directly (the oracle -- a "
        "diagonal phase equivalent of a multi-controlled-Z conditioned on "
        "the bit pattern of marked) followed by _diffusion(reg); it "
        "returns (register, iterations_used). run_grover(n, "
        "marked_bitstring, iterations) is the CLI-facing wrapper that "
        "converts the bitstring to an int, runs grover_search, and returns "
        "(found_bitstring, probability_of_marked, iterations_used) where "
        "found_bitstring is reg.most_probable() rendered via bitstring()."
    )

    doc.add_heading2("2.3 Quantum Fourier Transform -- src/quantum_toolkit/algorithms/qft.py")
    doc.add_paragraph(
        "apply_qft(reg, swap_output=True) implements the textbook QFT "
        "gate-by-gate: for j in range(n): reg.h(j), then for k in "
        "range(j+1, n): reg.cphase(k, j, theta) with theta = pi / "
        "2**(k-j) (a controlled-phase rotation, control qubit k, target "
        "qubit j, with angle halving as k moves further from j). If "
        "swap_output is True (the default), a final layer of "
        "reg.swap(j, n-1-j) for j in range(n//2) reverses the qubit order "
        "to match the standard convention that makes the resulting "
        "statevector equal (up to normalization) to numpy.fft.ifft of the "
        "input. qft(amplitudes, swap_output=True) is the array-in/array-out "
        "convenience wrapper: it infers n = round(log2(len(amplitudes))), "
        "constructs QuantumRegister(n, amplitudes) (validating the input "
        "is normalized), applies apply_qft, and returns reg.amps. "
        "classical_dft_reference(amplitudes) returns sqrt(N) * "
        "numpy.fft.ifft(amplitudes) as an independent classical "
        "cross-check target, per the identity QFT|j> = (1/sqrt(N)) "
        "sum_k exp(2*pi*i*j*k/N)|k>."
    )

    doc.add_heading2("2.4 Bernstein-Vazirani -- src/quantum_toolkit/algorithms/bernstein_vazirani.py")
    doc.add_paragraph(
        "run_bernstein_vazirani(n, secret) validates 0 <= secret < 2**n, "
        "builds QuantumRegister(n), calls reg.h_all(), applies "
        "reg.apply_diagonal_phase(lambda x: where(parity(x & secret) == 1, "
        "-1, 1)) -- the oracle f(x) = x.secret (mod 2), i.e. the same "
        "parity-of-AND construction as Deutsch-Jozsa's balanced_oracle -- "
        "then calls reg.h_all() again, and returns bitstring(reg."
        "most_probable(), n). Because the two Hadamard layers and the "
        "phase oracle deterministically rotate the amplitude of exactly "
        "the |secret> basis state to 1 (and every other basis state to "
        "0), most_probable() recovers the secret exactly on every run, "
        "with no repeated queries."
    )

    doc.add_heading2("2.5 Simulator core -- src/quantum_toolkit/simulator.py")
    doc.add_paragraph(
        "apply_gate(state, gate, qubits, n) is the single routine every "
        "gate method in QuantumRegister funnels through: it reshapes the "
        "flat length-2^n state into a (2,)*n tensor, transposes so the "
        "axes in qubits come first (perm = list(qubits) + other_axes), "
        "reshapes to (2**k, -1), left-multiplies by the k-qubit gate "
        "matrix, reshapes back, and un-transposes via argsort(perm) -- "
        "this is what lets a single function implement single-qubit "
        "gates, controlled two-qubit gates, and SWAP without ever building "
        "a 2^n x 2^n operator. popcount(x) is a vectorized bit-population "
        "count (via the standard SWAR bit-trick constants) and parity(x) "
        "= popcount(x) % 2 -- both operate on numpy uint64 arrays and are "
        "reused directly by the Deutsch-Jozsa and Bernstein-Vazirani "
        "oracle constructors."
    )

    # 3. Core data structures & gate reference
    doc.add_heading1("3. Core data structures & gate reference")
    doc.add_heading2("3.1 QuantumRegister")
    doc.add_paragraph(
        "class QuantumRegister (simulator.py). Fields: self.n (int, qubit "
        "count); self.amps (numpy complex ndarray, shape (2**n,), the "
        "statevector). __init__(n_qubits, amplitudes=None) defaults to "
        "zero_state(n_qubits) (|0...0>) or validates a supplied amplitude "
        "array has shape (2**n_qubits,) and is normalized "
        "(np.isclose(norm, 1.0)), raising ValueError otherwise."
    )
    doc.add_table(
        headers=["Method", "Signature", "Effect"],
        rows=[
            ["h", "h(q) -> self", "Apply Hadamard to qubit q"],
            ["x", "x(q) -> self", "Apply Pauli-X (bit flip) to qubit q"],
            ["y", "y(q) -> self", "Apply Pauli-Y to qubit q"],
            ["z", "z(q) -> self", "Apply Pauli-Z (phase flip) to qubit q"],
            ["phase", "phase(q, theta) -> self", "Apply single-qubit phase gate diag(1, e^{i theta}) to qubit q"],
            ["h_all", "h_all(qubits=None) -> self", "Apply Hadamard to every qubit (or the given subset)"],
            ["cnot", "cnot(control, target) -> self", "Apply controlled-NOT"],
            ["cz", "cz(control, target) -> self", "Apply controlled-Z"],
            ["cphase", "cphase(control, target, theta) -> self", "Apply controlled-phase diag(1,1,1,e^{i theta})"],
            ["swap", "swap(a, b) -> self", "Swap two qubits (no-op if a == b)"],
            ["apply_diagonal_phase", "apply_diagonal_phase(phase_fn) -> self", "Multiply amps elementwise by phase_fn(arange(2**n)) -- the oracle mechanism used by every algorithm"],
            ["probabilities", "probabilities() -> ndarray", "Return abs(amps)**2 for every basis state"],
            ["most_probable", "most_probable() -> int", "argmax of probabilities()"],
            ["most_probable_bitstring", "most_probable_bitstring() -> str", "most_probable() rendered as an n-bit binary string"],
            ["sample", "sample(shots, rng=None) -> dict", "Draw `shots` projective measurements, returns {basis_index: count}"],
            ["copy", "copy() -> QuantumRegister", "Deep-copy the register (new amps array)"],
        ],
    )
    doc.add_heading2("3.2 Gate reference")
    doc.add_table(
        headers=["Gate", "Matrix / effect", "Function / constant name"],
        rows=[
            ["Identity", "2x2 identity", "I2"],
            ["Hadamard", "(1/sqrt(2)) [[1,1],[1,-1]] -- creates superposition", "H"],
            ["Pauli-X", "[[0,1],[1,0]] -- bit flip", "X"],
            ["Pauli-Y", "[[0,-i],[i,0]]", "Y"],
            ["Pauli-Z", "[[1,0],[0,-1]] -- phase flip", "Z"],
            ["Phase", "diag(1, e^{i theta})", "phase_gate(theta)"],
            ["CNOT", "4x4, flips target iff control is 1", "CNOT"],
            ["CZ", "diag(1,1,1,-1)", "CZ"],
            ["SWAP", "4x4 permutation swapping the two qubits' amplitudes", "SWAP"],
            ["Controlled-phase", "diag(1,1,1,e^{i theta})", "controlled_phase(theta)"],
        ],
    )

    # 4. CLI command reference
    doc.add_heading1("4. CLI command reference")
    doc.add_paragraph(
        "Entry points: `python -m quantum_toolkit <command> [options]` "
        "(via __main__.py -> cli.main()) or the installed console script "
        "`quantum-toolkit <command> [options]` (declared in pyproject.toml "
        "as project.scripts). Parser construction is in cli.build_parser()."
    )
    doc.add_table(
        headers=["Command", "Parameters", "Description"],
        rows=[
            ["grover", "--qubits INT (required), --marked STR (required, n-bit binary string), --iterations INT (optional, default: theoretical optimum)", "Runs Grover's search for the given marked item; prints iterations used vs. theoretical optimum, the measured result, P(measure marked), and success"],
            ["dj / deutsch-jozsa", "--qubits INT (required), --oracle {constant,balanced} (default balanced), --value {0,1} (constant oracle's output, default random), --secret INT (balanced oracle's mask, default random), --seed INT", "Runs Deutsch-Jozsa against a constant or balanced oracle; prints the true oracle description, the verdict, and P(measure |0...0>)"],
            ["bv / bernstein-vazirani", "--qubits INT (required), --secret STR (required, n-bit binary string)", "Recovers the hidden secret string in a single query; prints the hidden secret, the recovered value, and success"],
            ["qft", "--qubits INT (required), --state STR (optional n-bit binary basis state to start from), --seed INT (optional, for random input)", "Applies the QFT to a basis state or random normalized input; prints the first 4 input amplitudes, first 4 QFT output amplitudes, first 4 classical DFT reference amplitudes, and the max absolute error between them"],
        ],
    )
    doc.add_heading2("4.1 Example invocations and real output")
    doc.add_paragraph("Example 1 -- Grover's search (from the repository README):")
    doc.add_code_block("$ python -m quantum_toolkit grover --qubits 4 --marked 1011")
    doc.add_code_block(
        "Grover's search over 16 items (4 qubits)\n"
        "  marked item        : 1011\n"
        "  iterations used    : 3 (theoretical optimum: 3)\n"
        "  measured result    : 1011\n"
        "  P(measure marked)  : 0.9613\n"
        "  success            : True"
    )
    doc.add_paragraph("Example 2 -- Deutsch-Jozsa against a balanced oracle:")
    doc.add_code_block("$ python -m quantum_toolkit dj --qubits 5 --oracle balanced --secret 22")
    doc.add_paragraph(
        "Prints the oracle description (\"balanced, f(x) = parity(x & "
        "10110)\"), verdict \"balanced\", and P(measure |0...0>) which will "
        "be exactly 0.0000 (interference guarantees the |0...0> amplitude "
        "vanishes for any balanced oracle)."
    )
    doc.add_paragraph("Example 3 -- Bernstein-Vazirani:")
    doc.add_code_block(
        "$ python -m quantum_toolkit bv --qubits 6 --secret 101101\n"
        "Bernstein-Vazirani over 6 qubits\n"
        "  hidden secret      : 101101\n"
        "  recovered (1 query): 101101\n"
        "  success            : True"
    )
    doc.add_paragraph("Example 4 -- QFT with a classical DFT cross-check:")
    doc.add_code_block("$ python -m quantum_toolkit qft --qubits 3 --seed 1")
    doc.add_paragraph(
        "Prints the first 4 (of 8) input amplitudes, the first 4 QFT "
        "output amplitudes, the first 4 classical DFT reference "
        "amplitudes computed independently via numpy.fft, and the max "
        "absolute error between the two, which is on the order of 1e-15 "
        "to 1e-16 (floating-point roundoff only) when the implementation "
        "is correct."
    )

    # 5. Sequence flows
    doc.add_heading1("5. Sequence flows / process flows")

    doc.add_heading2("5.1 Grover's search execution flow")
    doc.add_table(
        headers=["Step", "Operation", "Effect on statevector"],
        rows=[
            ["1", "QuantumRegister(n) then h_all()", "|0...0> -> uniform superposition over all 2^n basis states, each amplitude 1/sqrt(N)"],
            ["2", "For each of `iterations` rounds: flip sign of amps[marked]", "Oracle reflection -- the marked basis state's amplitude sign is inverted, all others unchanged"],
            ["3", "_diffusion(reg): h_all(); amps[0] *= -1; h_all()", "Diffusion reflection about the mean amplitude -- rotates the whole statevector, increasing the marked amplitude's magnitude"],
            ["4", "Repeat steps 2-3 optimal_iterations(n) times (or the override)", "Amplitude of the marked state grows towards its geometric maximum after each oracle+diffusion pair"],
            ["5", "reg.most_probable() / reg.probabilities()[marked]", "Measurement: sample the basis state with highest probability, report P(marked)"],
        ],
    )

    doc.add_heading2("5.2 Deutsch-Jozsa execution flow")
    doc.add_table(
        headers=["Step", "Operation", "Effect on statevector"],
        rows=[
            ["1", "QuantumRegister(n) then h_all()", "|0...0> -> uniform superposition"],
            ["2", "apply_diagonal_phase(oracle_fn)", "Each basis state |x> gets phase (-1)^f(x) -- phase kickback"],
            ["3", "h_all() again", "Interference: constant f cancels back to |0...0> exactly; balanced f drives |0...0>'s amplitude to exactly zero"],
            ["4", "Check probs[0] vs. 1.0", "Verdict: \"constant\" if P(|0...0>) is approx 1, else \"balanced\""],
        ],
    )

    doc.add_heading2("5.3 Bernstein-Vazirani execution flow")
    doc.add_table(
        headers=["Step", "Operation", "Effect on statevector"],
        rows=[
            ["1", "QuantumRegister(n) then h_all()", "|0...0> -> uniform superposition"],
            ["2", "apply_diagonal_phase(x -> (-1)^parity(x & secret))", "Each basis state |x> gets phase (-1)^(x.secret) -- phase kickback"],
            ["3", "h_all() again", "Interference concentrates all amplitude exactly onto |secret>"],
            ["4", "most_probable() -> bitstring", "Measurement recovers the secret string exactly, probability 1"],
        ],
    )

    doc.add_heading2("5.4 QFT execution flow")
    doc.add_table(
        headers=["Step", "Operation", "Effect on statevector"],
        rows=[
            ["1", "QuantumRegister(n, amplitudes) from an arbitrary normalized input (or a basis state)", "Initializes reg.amps to the given (already-normalized) input vector"],
            ["2", "For j in 0..n-1: h(j), then cphase(k, j, pi/2^(k-j)) for each k>j", "Builds up the Fourier-transformed phase relationships one qubit at a time (Hadamard + controlled-phase ladder)"],
            ["3", "Swap layer: swap(j, n-1-j) for j in 0..n//2-1", "Reverses qubit order to match the standard QFT output convention"],
            ["4", "Compare reg.amps against classical_dft_reference(amplitudes)", "Cross-check: result should equal sqrt(N)*numpy.fft.ifft(amplitudes) to within floating-point precision"],
        ],
    )

    # 6. Key algorithms & business logic
    doc.add_heading1("6. Key algorithms & business logic")
    doc.add_heading2("6.1 Grover iteration-count formula")
    doc.add_paragraph(
        "optimal_iterations(n) (grover.py) computes N = 2**n, the "
        "per-iteration rotation angle theta = 2*asin(1/sqrt(N)), and "
        "returns k* = max(1, round(pi/(2*theta) - 0.5)). This is the exact "
        "integer iteration count that lands closest to a total rotation of "
        "pi/2 (maximum overlap with the marked state), which the module's "
        "docstring notes can differ from the commonly-cited asymptotic "
        "estimate round(pi/4*sqrt(N)) by one iteration at small N -- using "
        "the naive estimate there can overshoot and noticeably hurt the "
        "success probability. The test suite "
        "(test_iteration_count_matches_theoretical_optimum) checks this "
        "formula directly, and "
        "test_more_iterations_than_optimal_can_reduce_success_probability "
        "verifies the overshoot behavior."
    )
    doc.add_heading2("6.2 QFT matrix construction")
    doc.add_paragraph(
        "The QFT is never built as a single 2^n x 2^n matrix. Instead "
        "apply_qft applies, for each qubit j in order, one Hadamard "
        "followed by controlled-phase gates controlled by every "
        "later qubit k (j < k < n) with angle theta = pi / 2**(k-j) -- "
        "so the angle halves for each additional qubit of separation, "
        "matching the textbook QFT circuit exactly. A final swap layer "
        "(swap(j, n-1-j) for j < n//2) reverses qubit order. The total "
        "gate count is O(n) Hadamards + O(n^2) controlled-phase gates, "
        "which is the source of the QFT's exponential gate-count "
        "advantage over the O(N log N) classical FFT. Correctness is "
        "cross-checked against classical_dft_reference(amplitudes) = "
        "sqrt(N) * numpy.fft.ifft(amplitudes), following the identity "
        "QFT|j> = (1/sqrt(N)) sum_k exp(2*pi*i*j*k/N)|k>."
    )
    doc.add_heading2("6.3 Deutsch-Jozsa oracle-distinction logic")
    doc.add_paragraph(
        "constant_oracle(value) returns a phase function that is "
        "identically +1 or -1 for every input (a valid constant f). "
        "balanced_oracle(secret) returns phase_fn(x) = "
        "(-1)^parity(x & secret), which is 0 on exactly half of "
        "{0,1}^n and 1 on the other half for any nonzero secret (raises "
        "ValueError if secret == 0, since that would make f identically "
        "0, i.e. constant, not balanced). The decision rule after the "
        "H^n -> oracle -> H^n circuit is purely probs[0] approx 1.0 "
        "(atol=1e-9) => \"constant\", else \"balanced\" -- exploiting the "
        "mathematical guarantee that these are the only two possible "
        "outcomes under the algorithm's promise."
    )
    doc.add_heading2("6.4 Bernstein-Vazirani recovery logic")
    doc.add_paragraph(
        "The oracle f(x) = x.secret (mod 2) is realized as phase_fn(x) = "
        "(-1)^parity(x & secret), identical in form to Deutsch-Jozsa's "
        "balanced_oracle. After H^n -> oracle -> H^n, the resulting "
        "statevector has amplitude exactly 1 (up to global phase) at "
        "basis index `secret` and 0 everywhere else -- a consequence of "
        "the Hadamard transform's self-duality under XOR/dot-product "
        "structure. run_bernstein_vazirani therefore recovers the secret "
        "with reg.most_probable(), which is exact (not merely "
        "high-probability) in every test case, including the edge cases "
        "secret=0 and secret=2**n-1 explicitly covered by "
        "test_all_zero_secret and test_all_one_secret."
    )

    # 7. Validation & error handling
    doc.add_heading1("7. Validation & error handling")
    doc.add_bullets([
        "CLI-level bitstring validation: grover's --marked and bv's --secret are checked for exact length n and a {0,1}-only alphabet before use; a mismatch prints an error to stderr and returns exit code 1 without constructing a circuit (cli.py, _cmd_grover / _cmd_bv).",
        "QuantumRegister construction validates any explicitly supplied amplitude array: wrong shape (not (2**n,)) or non-normalized norm (not np.isclose(norm, 1.0)) raises ValueError immediately (simulator.py, __init__), covered by test_register_rejects_non_normalized_input and test_register_rejects_wrong_length.",
        "grover_search validates 0 <= marked < 2**n and raises ValueError otherwise (test_grover_search_rejects_out_of_range_marked_item).",
        "balanced_oracle raises ValueError for secret == 0 (would silently produce a constant, not balanced, function) (test_balanced_oracle_rejects_zero_secret); constant_oracle raises ValueError for any value not in {0, 1} (test_constant_oracle_rejects_bad_value).",
        "run_bernstein_vazirani validates 0 <= secret < 2**n and raises ValueError otherwise (test_rejects_secret_too_large).",
        "Known gaps: qubit-count itself is never upper-bounded by the library -- a user can pass --qubits 30 and the process will simply run out of memory or take a very long time (this is flagged prominently in the README rather than enforced in code); the CLI's --qubits argument also accepts 0 or negative values without an explicit guard, relying on downstream numpy errors rather than a friendly message.",
    ])

    # 8. Non-functional implementation details
    doc.add_heading1("8. Non-functional implementation details")
    doc.add_paragraph(
        "Statevector size grows as 2^n complex128 values (16 bytes each): "
        "256 bytes at n=5, ~1 MB at n=16, ~16 MB at n=20, and roughly 16 GB "
        "at n=30 -- the exact exponential blowup the README calls out as "
        "fundamental to classical statevector simulation, not specific to "
        "this implementation. apply_gate's reshape/transpose/contract "
        "approach avoids ever allocating a 2^n x 2^n gate operator (which "
        "would be far worse), but each call still touches the full "
        "2^n-length array, so per-gate cost is O(2^n); QFT's O(n^2) gate "
        "count multiplies that by roughly n^2/2 controlled-phase "
        "applications plus n Hadamards. Numerical precision is numpy's "
        "default complex128 throughout; probabilities() and sample() "
        "explicitly renormalize (probs / probs.sum()) before drawing "
        "samples to absorb floating-point drift from repeated unitary "
        "applications, and the QFT cross-check test tolerates roundoff on "
        "the order of 1e-9 to 1e-12 rather than expecting bit-exact "
        "equality with the numpy.fft reference."
    )

    # 8 (Appendix section number continues as 9 per template's section 8 -> appendix numbered as 8. Following instructions: Appendix as section 8)
    doc.add_heading1("9. Appendix")
    doc.add_heading2("9.1 Repo module/file map")
    doc.add_code_block(
        "Darviq-Quantum/\n"
        "  README.md                       # algorithm write-ups, scaling-limit guidance, CLI examples\n"
        "  pyproject.toml                  # package metadata, deps, console-script entry point\n"
        "  requirements.txt\n"
        "  .github/workflows/ci.yml        # test + CLI smoke-test matrix (Python 3.9/3.11/3.12)\n"
        "  src/quantum_toolkit/\n"
        "    __init__.py                   # package docstring, __version__\n"
        "    __main__.py                   # `python -m quantum_toolkit` entry point\n"
        "    cli.py                        # argparse subcommands: grover, dj, bv, qft\n"
        "    simulator.py                  # gate matrices, apply_gate, QuantumRegister, bit utils\n"
        "    qiskit_adapter.py              # optional Qiskit bridge (bv + grover only, unused by core)\n"
        "    algorithms/\n"
        "      __init__.py\n"
        "      deutsch_jozsa.py            # constant_oracle, balanced_oracle, run_deutsch_jozsa\n"
        "      grover.py                   # optimal_iterations, grover_search, run_grover\n"
        "      qft.py                      # apply_qft, qft, classical_dft_reference\n"
        "      bernstein_vazirani.py       # run_bernstein_vazirani\n"
        "  tests/\n"
        "    test_simulator.py             # 12 tests: gates, apply_gate, register validation, bit utils\n"
        "    test_grover.py                # 5 tests: success probability, iteration optimum, validation\n"
        "    test_deutsch_jozsa.py         # 5 tests: constant/balanced detection, oracle validation\n"
        "    test_qft.py                   # 4 tests: DFT cross-check, basis states, uniform superposition\n"
        "    test_bernstein_vazirani.py    # 5 tests: secret recovery, edge cases, validation"
    )
    doc.add_heading2("9.2 Test coverage summary")
    doc.add_paragraph(
        "The pytest suite (tests/, 302 lines total) contains 31 tests "
        "across 5 files, all verifying each algorithm and simulator "
        "primitive against a known classical or theoretical answer rather "
        "than only internal self-consistency:"
    )
    doc.add_table(
        headers=["File", "Tests", "What it verifies"],
        rows=[
            ["test_simulator.py", "12", "Zero state, Hadamard superposition, X-gate bit flip, double-X identity, CNOT Bell state, SWAP, normalization after random gate sequences, apply_gate vs. manual Kronecker-product construction, bitstring formatting, popcount/parity, and rejection of non-normalized or wrong-length register input"],
            ["test_grover.py", "5", "Marked item found with high probability across qubit counts, iteration count matches optimal_iterations, out-of-range marked item rejected, custom iteration override honored, and that over-iterating past the optimum can reduce success probability"],
            ["test_deutsch_jozsa.py", "5", "Constant oracle detected for both values, balanced oracle detected across random secrets and qubit counts, invalid constant value rejected, zero secret rejected, and probabilities always sum to 1"],
            ["test_qft.py", "4", "QFT output matches classical_dft_reference on random states and on basis states, QFT of |0...0> yields the uniform superposition, and a round-trip/unitary consistency check"],
            ["test_bernstein_vazirani.py", "5", "Exact recovery for all secrets at small n, exact recovery for random secrets, the all-zero-secret edge case, the all-one-secret edge case, and rejection of an out-of-range secret"],
        ],
    )
    doc.add_paragraph(
        "CI (.github/workflows/ci.yml) runs this full suite plus a live "
        "smoke test of all four CLI subcommands on Python 3.9, 3.11, and "
        "3.12 for every push/PR to main."
    )
    doc.add_heading2("9.3 Change history")
    doc.add_table(
        headers=["Version", "Date", "Description"],
        rows=[["1.0", DATE, "Initial low-level design document"]],
    )

    return doc


if __name__ == "__main__":
    hld = build_hld()
    hld.save(os.path.join(DOCS_DIR, "Darviq_Quantum_High_Level_Design.docx"))
    print("Saved HLD")

    lld = build_lld()
    lld.save(os.path.join(DOCS_DIR, "Darviq_Quantum_Low_Level_Design.docx"))
    print("Saved LLD")
