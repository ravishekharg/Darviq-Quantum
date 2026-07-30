"""Command-line interface for quantum_toolkit.

Examples
--------
::

    python -m quantum_toolkit grover --qubits 4 --marked 1011
    python -m quantum_toolkit dj --qubits 5 --oracle balanced --secret 10110
    python -m quantum_toolkit bv --qubits 6 --secret 101101
    python -m quantum_toolkit qft --qubits 3
"""

from __future__ import annotations

import argparse
import math
import random
import sys

import numpy as np

from quantum_toolkit.algorithms.bernstein_vazirani import run_bernstein_vazirani
from quantum_toolkit.algorithms.deutsch_jozsa import balanced_oracle, constant_oracle, run_deutsch_jozsa
from quantum_toolkit.algorithms.grover import optimal_iterations, run_grover
from quantum_toolkit.algorithms.qft import classical_dft_reference, qft


def _cmd_grover(args: argparse.Namespace) -> int:
    n = args.qubits
    marked = args.marked
    if len(marked) != n or any(c not in "01" for c in marked):
        print(f"error: --marked must be a {n}-bit binary string", file=sys.stderr)
        return 1

    found, prob, iterations = run_grover(n, marked, iterations=args.iterations)
    print(f"Grover's search over {2 ** n} items ({n} qubits)")
    print(f"  marked item        : {marked}")
    print(f"  iterations used    : {iterations} (theoretical optimum: {optimal_iterations(n)})")
    print(f"  measured result    : {found}")
    print(f"  P(measure marked)  : {prob:.4f}")
    print(f"  success            : {found == marked}")
    return 0


def _cmd_dj(args: argparse.Namespace) -> int:
    n = args.qubits
    rng = random.Random(args.seed)

    if args.oracle == "constant":
        value = args.value if args.value is not None else rng.randint(0, 1)
        oracle_fn = constant_oracle(value)
        description = f"constant, f(x) = {value}"
    else:
        secret = args.secret if args.secret is not None else rng.randint(1, 2 ** n - 1)
        oracle_fn = balanced_oracle(secret)
        description = f"balanced, f(x) = parity(x & {secret:0{n}b})"

    verdict, probs = run_deutsch_jozsa(n, oracle_fn)
    print(f"Deutsch-Jozsa over {n} qubits")
    print(f"  true oracle        : {description}")
    print(f"  verdict            : {verdict}")
    print(f"  P(measure |0...0>) : {probs[0]:.4f}")
    return 0


def _cmd_bv(args: argparse.Namespace) -> int:
    n = args.qubits
    secret_str = args.secret
    if len(secret_str) != n or any(c not in "01" for c in secret_str):
        print(f"error: --secret must be a {n}-bit binary string", file=sys.stderr)
        return 1
    secret = int(secret_str, 2)

    recovered = run_bernstein_vazirani(n, secret)
    print(f"Bernstein-Vazirani over {n} qubits")
    print(f"  hidden secret      : {secret_str}")
    print(f"  recovered (1 query): {recovered}")
    print(f"  success            : {recovered == secret_str}")
    return 0


def _cmd_qft(args: argparse.Namespace) -> int:
    n = args.qubits
    N = 2 ** n

    if args.state is not None:
        state_str = args.state
        if len(state_str) != n or any(c not in "01" for c in state_str):
            print(f"error: --state must be a {n}-bit binary string", file=sys.stderr)
            return 1
        amplitudes = np.zeros(N, dtype=complex)
        amplitudes[int(state_str, 2)] = 1.0
    else:
        rng = np.random.default_rng(args.seed)
        amplitudes = rng.normal(size=N) + 1j * rng.normal(size=N)
        amplitudes = amplitudes / np.linalg.norm(amplitudes)

    output = qft(amplitudes)
    reference = classical_dft_reference(amplitudes)
    max_error = float(np.max(np.abs(output - reference)))

    print(f"QFT over {n} qubits ({N}-dim statevector)")
    print(f"  input amplitudes[:4]      : {np.round(amplitudes[:4], 4)}")
    print(f"  QFT output[:4]            : {np.round(output[:4], 4)}")
    print(f"  classical DFT reference[:4]: {np.round(reference[:4], 4)}")
    print(f"  max |QFT - classical DFT| : {max_error:.2e}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quantum_toolkit", description="Run canonical quantum algorithms on a numpy statevector simulator.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_grover = sub.add_parser("grover", help="Grover's unstructured search")
    p_grover.add_argument("--qubits", type=int, required=True, help="number of qubits (search space size = 2**qubits)")
    p_grover.add_argument("--marked", type=str, required=True, help="marked item as a binary string, e.g. 1011")
    p_grover.add_argument("--iterations", type=int, default=None, help="override iteration count (default: theoretical optimum)")
    p_grover.set_defaults(func=_cmd_grover)

    p_dj = sub.add_parser("dj", help="Deutsch-Jozsa constant-vs-balanced test", aliases=["deutsch-jozsa"])
    p_dj.add_argument("--qubits", type=int, required=True)
    p_dj.add_argument("--oracle", choices=["constant", "balanced"], default="balanced")
    p_dj.add_argument("--value", type=int, choices=[0, 1], default=None, help="constant oracle's fixed output (default: random)")
    p_dj.add_argument("--secret", type=int, default=None, help="balanced oracle's secret mask, as an integer (default: random)")
    p_dj.add_argument("--seed", type=int, default=None)
    p_dj.set_defaults(func=_cmd_dj)

    p_bv = sub.add_parser("bv", help="Bernstein-Vazirani hidden-string recovery", aliases=["bernstein-vazirani"])
    p_bv.add_argument("--qubits", type=int, required=True)
    p_bv.add_argument("--secret", type=str, required=True, help="hidden bitstring, e.g. 101101")
    p_bv.set_defaults(func=_cmd_bv)

    p_qft = sub.add_parser("qft", help="Quantum Fourier Transform demo + classical DFT cross-check")
    p_qft.add_argument("--qubits", type=int, required=True)
    p_qft.add_argument("--state", type=str, default=None, help="start from basis state |state> instead of a random input")
    p_qft.add_argument("--seed", type=int, default=None)
    p_qft.set_defaults(func=_cmd_qft)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
