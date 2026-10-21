"""
tests/test_week4_contract.py

Eight tests. You did not write them and you may not change them.

None of them asserts that you removed seventeen rows, because your audit may have
reached a different conclusion from mine and it is allowed to. What they check is
that whatever you removed, you can account for, that cleaning your own output
removes nothing more, and that your two measurements come with a spread.

    python -m pytest -q tests/test_week4_contract.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
CLEANING = ROOT / "src" / "cleaning.py"
LEAK_LAB = ROOT / "src" / "leak_lab.py"
OUT = ROOT / "outputs"
JOINED = ROOT / "data" / "orders_joined.csv"


def _run(script: str, cwd: Path = ROOT):
    return subprocess.run([sys.executable, f"src/{script}"], cwd=cwd,
                          capture_output=True, text=True)


@pytest.fixture(scope="module")
def cleaned():
    if not JOINED.exists():
        pytest.fail(
            "data/orders_joined.csv is missing. After make ingest, run "
            "cp outputs/orders_joined.csv data/, or copy it from the "
            "week04_thursday folder. docs/week04_brief.md has both.")
    if not CLEANING.exists():
        pytest.fail("src/cleaning.py does not exist yet")
    r = _run("cleaning.py")
    if r.returncode != 0:
        pytest.fail(f"src/cleaning.py exited {r.returncode}\n{r.stderr[-2000:]}")
    return pd.read_csv(OUT / "orders_clean.csv")


def test_cleaning_runs_and_writes_both_files(cleaned):
    assert (OUT / "orders_clean.csv").exists()
    assert (OUT / "cleaning_ledger.csv").exists(), "write outputs/cleaning_ledger.csv"


def test_the_ledger_accounts_for_every_row(cleaned):
    """
    The one that matters. However many rows you removed, the ledger has to add up
    to that number. A pipeline that loses rows it cannot name is one nobody can
    audit later, including you.
    """
    before = len(pd.read_csv(JOINED))
    after = len(cleaned)
    ledger = pd.read_csv(OUT / "cleaning_ledger.csv")
    assert "removed" in ledger.columns, (
        "the ledger needs a removed column, the number of rows each step took out")
    claimed = int(ledger["removed"].sum())
    assert claimed == before - after, (
        f"{before - after} rows left the pipeline and the ledger accounts for "
        f"{claimed}. Some step is removing rows without recording it."
    )


def test_every_step_gives_a_reason(cleaned):
    ledger = pd.read_csv(OUT / "cleaning_ledger.csv")
    assert "reason" in ledger.columns, "the ledger needs a reason column"
    blank = ledger["reason"].isna() | (ledger["reason"].astype(str).str.strip() == "")
    assert not blank.any(), "a step removed rows without saying why"


def test_every_cleaning_function_has_a_docstring():
    """
    The reason is the part somebody needs in March. The code is the part they can
    read for themselves.
    """
    if not CLEANING.exists():
        pytest.fail("src/cleaning.py does not exist yet")
    # module-level functions only. Helper methods inside a class are yours to
    # organise; the cleaning decisions are the ones that have to carry a reason.
    tree = ast.parse(CLEANING.read_text())
    undocumented = [
        n.name for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and not n.name.startswith("_")
        and n.name not in {"main"}
        and ast.get_docstring(n) is None
    ]
    assert not undocumented, f"functions with no docstring: {undocumented}"


def test_cleaning_a_clean_table_removes_nothing(cleaned, tmp_path):
    """
    Week 1's rule, that running a thing twice changes nothing, applied to
    cleaning. A copy of your repository is given your cleaned table as though it
    were the joined one, and a second pass has to remove no rows at all.

    A rule that passes says what a value can be. A rule that fails is usually
    measured against the rows in front of it, a z score or a quantile, and it
    removes something new from every table it meets, tomorrow's orders included.
    An earlier version of this test only ran the script twice on the same input,
    which a rule like that passes.
    """
    copy = tmp_path / "repo"
    shutil.copytree(ROOT / "src", copy / "src")
    shutil.copytree(ROOT / "data", copy / "data")
    shutil.copy(OUT / "orders_clean.csv", copy / "data" / "orders_joined.csv")
    r = _run("cleaning.py", cwd=copy)
    assert r.returncode == 0, (
        f"src/cleaning.py failed when it was given its own output\n{r.stderr[-2000:]}")
    again = pd.read_csv(copy / "outputs" / "orders_clean.csv")
    assert len(again) == len(cleaned), (
        f"cleaning your cleaned table removed {len(cleaned) - len(again)} more rows. "
        "A rule that keeps finding new rows to remove is measured against the "
        "table, not against what a value can be. Move it out of the cleaning, or "
        "write it as a fixed limit and say why in its docstring."
    )


def test_you_did_not_fill_the_unexplained_column(cleaned):
    """
    The 46 blank marketing_opt_in values have no source. Filling them reproduces,
    by a different route, the exact fault Week 2 was about.

    If you have a reasoned argument for filling them, you will have to make it to
    a human, because this test does not accept one.
    """
    if "marketing_opt_in" not in cleaned.columns:
        pytest.skip("column not carried through")
    assert cleaned["marketing_opt_in"].isna().sum() > 0, (
        "marketing_opt_in has no blanks left. Either you dropped every row that "
        "had one, or you filled them. Both need to be in your write-up."
    )


def test_you_did_not_edit_the_real_dataset():
    p = ROOT / "data" / "penguins_raw.csv"
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    assert got == "144f623143c9360f", "data/penguins_raw.csv has been modified."


def test_leak_lab_reports_both_measurements_with_a_spread(cleaned):
    """
    Task C. Both measurements, each with its spread over the seeds, in
    outputs/leak_lab.json. The keys are yours. The test checks that both are
    there and that a spread is reported, not that you used my words or found my
    numbers.
    """
    if not LEAK_LAB.exists():
        pytest.fail("src/leak_lab.py does not exist yet")
    r = _run("leak_lab.py")
    assert r.returncode == 0, f"src/leak_lab.py exited {r.returncode}\n{r.stderr[-2000:]}"
    path = OUT / "leak_lab.json"
    assert path.exists(), "write outputs/leak_lab.json"
    text = path.read_text()
    json.loads(text)
    text = text.lower()
    assert "scaler" in text, "the scaler measurement is missing, or never says scaler"
    assert "outlier" in text, "the outlier measurement is missing, or never says outlier"
    assert any(w in text for w in ("sd", "std", "spread", "stdev")), (
        "report a spread, the standard deviation over your seeds, beside each "
        "number. A difference without its spread cannot be read.")
