"""
src/verify.py

This script is supplied and is not yours to write. It is what make verify runs,
and it is written in Python so that it also runs on Windows, where make is
usually missing.

It runs this week's script twice, hashes the files it writes, prints both sets
of hashes and exits with an error when the two runs differ, because a check that
cannot fail is not a check.

    python src/verify.py
"""

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ["src/evaluate.py"]
OUTPUTS = ["outputs/evaluation.json", "outputs/evaluation_folds.csv"]


def run_once():
    for script in SCRIPTS:
        r = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{script} exited {r.returncode}")
            print(r.stderr[-2000:])
            sys.exit(1)
    hashes = []
    for out in OUTPUTS:
        path = ROOT / out
        if not path.exists():
            print(f"{out} was not written")
            sys.exit(1)
        hashes.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {out}")
    return hashes


first = run_once()
second = run_once()
print("\n".join(first + second))
if first == second:
    print("the two runs match")
else:
    print("THE TWO RUNS DIFFER. Something in your code is not seeded,")
    print("or depends on the order a set or dict happened to be in,")
    print("or writes the time it ran.")
    sys.exit(1)
