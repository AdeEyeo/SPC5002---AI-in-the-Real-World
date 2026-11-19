"""
tests/test_week8_contract.py

These six tests were not written by you and you may not change them.

None of them asserts a score, since your cleaning and your features are yours.
They check that src/evaluate.py runs, that its 25 folds really are 25 different
folds, that every floor is the share of returns in its own test fold, that the
paired differences and the wins match the per-fold scores, that two runs agree,
and that the evaluation note exists with its five sections.

    python -m pytest -q tests/test_week8_contract.py
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "evaluate.py"
REPORT = ROOT / "outputs" / "evaluation.json"
FOLDS = ROOT / "outputs" / "evaluation_folds.csv"
NOTE = ROOT / "docs" / "evaluation_note.md"
PIPELINE = "your pipeline"


@pytest.fixture(scope="module")
def report():
    if not (ROOT / "data" / "orders_clean.csv").exists():
        pytest.fail("data/orders_clean.csv is missing. Week 5's brief says how to copy it in.")
    if not (ROOT / "src" / "features.py").exists():
        pytest.fail("src/features.py is missing. src/evaluate.py builds on your Week 5 pipeline.")
    if not SCRIPT.exists():
        pytest.fail("src/evaluate.py is missing. It is in lab_week08.zip.")
    r = subprocess.run([sys.executable, "src/evaluate.py"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.fail(f"src/evaluate.py exited {r.returncode}\n{(r.stdout + r.stderr)[-2000:]}")
    return json.loads(REPORT.read_text())


@pytest.fixture(scope="module")
def rows(report):
    with FOLDS.open() as f:
        return [{**r, "seed": int(r["seed"]), "fold": int(r["fold"]), "floor": float(r["floor"]),
                 "roc_auc": float(r["roc_auc"]), "pr_auc": float(r["pr_auc"])} for r in csv.DictReader(f)]


def test_evaluate_runs_and_writes_its_report(report):
    for key in ("base_rate", "folds", "candidates", "paired_with_your_pipeline"):
        assert key in report, f"outputs/evaluation.json has no {key}. Did you change main()?"
    assert PIPELINE in report["candidates"], f'the candidates should include "{PIPELINE}"'
    for name, c in report["candidates"].items():
        assert c["roc_auc"]["sd"] > 0, f"{name} has an sd of 0 over its folds. Every score needs its spread."


def test_the_25_folds_are_different_folds(rows):
    mine = [r for r in rows if r["candidate"] == PIPELINE]
    assert len(mine) == 25, f"your pipeline has {len(mine)} fold scores, and 5 folds shuffled 5 times make 25"
    by_seed = defaultdict(list)
    for r in sorted(mine, key=lambda r: (r["seed"], r["fold"])):
        by_seed[r["seed"]].append(r["roc_auc"])
    assert len({tuple(v) for v in by_seed.values()}) == 5, (
        "every shuffle gave the same five folds, so the 25 scores are 5 scores five times. "
        "StratifiedKFold needs random_state=seed inside the loop in folds().")


def test_each_floor_is_its_own_test_folds_share(report, rows):
    floors = [r["floor"] for r in rows]
    assert all(0 < f < 1 for f in floors), "a floor is a share of orders, between 0 and 1"
    assert len(set(floors)) > 1, (
        f"every fold has the same floor, {floors[0]}, the base rate of all the orders. The floor is "
        "the share of returns in that fold's own test orders, y[test].mean().")
    # a test fold holds a fifth of the orders, so its share of returns is a whole number
    # of returns out of that many, to within the four places the file keeps
    n = report["orders"] // 5
    whole = [min(abs(f * m - round(f * m)) for m in (n, n + 1)) < 0.03 for f in floors]
    assert all(whole), (
        "some floors are not a whole number of returns out of a test fold's orders, so they look "
        "like the share in the training orders. The floor is the test fold's share, y[test].mean().")
    base = report["base_rate"]
    assert all(abs(f - base) < 0.02 for f in floors), (
        "with stratified folds every test fold's share of returns should be close to the base rate")


def test_the_paired_differences_and_the_wins(report, rows):
    score = {(r["seed"], r["fold"], r["candidate"]): r["roc_auc"] for r in rows}
    keys = sorted({(r["seed"], r["fold"]) for r in rows})
    paired = report["paired_with_your_pipeline"]
    assert paired, "paired_with_your_pipeline is empty"
    per_fold = {name: [score[(s, k, name)] - score[(s, k, PIPELINE)] for s, k in keys] for name in paired}
    # the direction first, for every candidate, because a candidate that ties your
    # pipeline has no sign to read
    for name, p in paired.items():
        mean = sum(per_fold[name]) / len(per_fold[name])
        assert p["folds"] == 25, f"{name} is compared on {p['folds']} folds, and there are 25"
        if abs(p["difference"] + mean) < 0.001 and abs(mean) > 0.001:
            pytest.fail(f"for {name} that is your pipeline minus the candidate. Subtract your "
                        "pipeline from the candidate, so a positive difference means the candidate is higher.")
        assert abs(p["difference"] - mean) < 0.001, (
            f"for {name} the difference is {p['difference']}, and the per-fold scores give {mean:.4f}")
    for name, p in paired.items():
        # the file holds scores rounded to four places, so a difference within
        # 0.0001 of zero may have been either side of it
        sure = sum(d > 0.0001 for d in per_fold[name])
        maybe = sum(d > -0.0001 for d in per_fold[name])
        if not sure <= p["wins"] <= maybe and 25 - maybe <= p["wins"] <= 25 - sure:
            pytest.fail(f"for {name}, {p['wins']} is the number of folds your pipeline is higher. "
                        "Count the folds where the difference is above 0.")
        assert sure <= p["wins"] <= maybe, (
            f"for {name} wins is {p['wins']}, and the candidate is higher in {sure} folds")


def test_evaluate_is_seeded(report):
    """The same script twice gives the same files, because every shuffle has a seed."""
    first = REPORT.read_bytes(), FOLDS.read_bytes()
    subprocess.run([sys.executable, "src/evaluate.py"], cwd=ROOT, capture_output=True, text=True)
    assert (REPORT.read_bytes(), FOLDS.read_bytes()) == first, "two runs of src/evaluate.py gave different files"


def test_evaluation_note_has_its_five_parts():
    if not NOTE.exists():
        pytest.fail("docs/evaluation_note.md does not exist yet. Start from docs/evaluation_template.md.")
    text = NOTE.read_text()
    headings = re.findall(r"^##\s+\d", text, flags=re.M)
    assert len(headings) >= 5, f"the note has {len(headings)} numbered parts, and five are asked for"
    words = len(re.sub(r"<!--.*?-->", "", text, flags=re.S).split())
    assert words >= 400, (
        f"the note has {words} words outside the template's comments. One to two pages is about "
        "500 to 1,000.")
