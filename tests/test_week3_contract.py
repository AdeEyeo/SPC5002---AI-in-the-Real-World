"""
tests/test_week3_contract.py

Seven tests. You did not write them and you may not change them. None asserts a
number is correct; they check that your profile covers everything and that your
constraints are capable of failing.

    python -m pytest -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "src" / "profile.py"
CONSTRAINTS = ROOT / "src" / "constraints.py"
OUT = ROOT / "outputs"
PENGUINS = ROOT / "data" / "penguins_raw.csv"


def _run(script: str):
    return subprocess.run([sys.executable, f"src/{script}"], cwd=ROOT,
                          capture_output=True, text=True)


@pytest.fixture(scope="module")
def profiled():
    if not PROFILE.exists():
        pytest.fail("src/profile.py does not exist yet")
    r = _run("profile.py")
    if r.returncode != 0:
        pytest.fail(f"src/profile.py exited {r.returncode}\n{r.stderr[-2000:]}")
    return json.loads((OUT / "profile.json").read_text())


def test_profile_runs_and_writes_json(profiled):
    assert profiled


def test_profile_covers_every_column_of_both_datasets(profiled):
    """
    A profile that skips a column is an opinion about which columns matter.

    Both means both. An earlier version of this checked only the penguins, so a
    profile that ignored your own joined table passed under a name that said
    otherwise.
    """
    flat = json.dumps(profiled)
    wanted = {"data/penguins_raw.csv": list(pd.read_csv(PENGUINS, nrows=1).columns)}
    joined = ROOT / "data" / "orders_joined.csv"
    if joined.exists():
        wanted[str(joined.relative_to(ROOT))] = list(pd.read_csv(joined, nrows=1).columns)
    else:
        pytest.fail(
            "data/orders_joined.csv is missing, so half of this week cannot be "
            "profiled. Run make ingest, then cp outputs/orders_joined.csv data/"
        )
    for dataset, cols in wanted.items():
        missing = [c for c in cols if c not in flat]
        assert not missing, f"columns of {dataset} absent from your profile: {missing}"


def test_profile_reports_the_three_questions(profiled):
    """
    Type, cardinality, missing count. For every column.

    The test is that you answered the question, not that you used my word for
    it. An earlier version demanded the literal string "distinct" while the
    brief asked for "cardinality", so a profile that did exactly what it was
    told failed.
    """
    flat = json.dumps(profiled).lower()
    questions = {
        "the type of the column": ["type", "dtype"],
        "how many distinct values it takes": ["distinct", "cardinality", "unique", "nunique"],
        "how many are missing": ["missing", "null", "nan", "na_count"],
    }
    for question, words in questions.items():
        assert any(w in flat for w in words), (
            f"your profile never says {question}. Any of {words} would do.")


def test_constraints_run(profiled):
    if not CONSTRAINTS.exists():
        pytest.fail("src/constraints.py does not exist yet")
    r = _run("constraints.py")
    assert r.returncode == 0, r.stderr[-2000:]
    assert (OUT / "violations.csv").exists(), "write outputs/violations.csv"


def test_constraints_found_something(profiled):
    _run("constraints.py")
    v = pd.read_csv(OUT / "violations.csv")
    assert len(v) > 0, (
        "your constraints passed on a table with seventeen impossible rows in it. "
        "A constraint that never fails is a comment."
    )


def test_every_constraint_carries_a_reason():
    """
    A constraint you cannot justify is an opinion, and opinions do not belong in
    an assertion. Each one needs a reason attached, in the code, in words.
    """
    src = CONSTRAINTS.read_text() if CONSTRAINTS.exists() else ""

    # A reason is prose. An earlier version of this counted any line containing
    # a quote character, so pd.read_csv("orders.csv") scored as a justification
    # and a file with no reasons in it at all passed.
    import io, tokenize
    prose = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                words = tok.string.lstrip("#").split()
                if len(words) >= 4:
                    prose.append(tok.string.strip())
            elif tok.type == tokenize.STRING:
                body = tok.string.strip("\"'brfuRFU \n")
                if len(body.split()) >= 4:
                    prose.append(body[:60])
    except (tokenize.TokenError, IndentationError):
        pytest.fail("src/constraints.py does not parse")

    assert len(prose) >= 5, (
        f"src/constraints.py carries {len(prose)} lines of actual prose, and "
        "every constraint needs a one-line reason saying why the rule is the "
        "rule. A comment or a docstring of four words or more counts; a file "
        "path in quotes does not."
    )


def test_you_did_not_edit_the_real_dataset():
    """
    It is somebody's fieldwork. If you need it changed, change it in your code and
    say so, the way you would if you could not reach the person who collected it.
    """
    import hashlib
    got = hashlib.sha256(PENGUINS.read_bytes()).hexdigest()[:16]
    assert got == "144f623143c9360f", (
        "data/penguins_raw.csv has been modified. Restore the original."
    )
