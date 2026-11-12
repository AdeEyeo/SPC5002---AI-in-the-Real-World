"""
tests/test_week6_contract.py

Six tests. You did not write them and you may not change them.

None asserts a score, because your cleaning and your features are yours. They
check that src/imbalance.py runs and reports what Part A asks for, that the
threshold it found really matches the class-weighted model, and that the
Milestone 2 note exists with its six parts.

    python -m pytest -q tests/test_week6_contract.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "imbalance.py"
REPORT = ROOT / "outputs" / "imbalance.json"
NOTE = ROOT / "docs" / "milestone2_preprocessing.md"


@pytest.fixture(scope="module")
def report():
    if not (ROOT / "data" / "orders_clean.csv").exists():
        pytest.fail("data/orders_clean.csv is missing. Week 5's brief says how to copy it in.")
    if not (ROOT / "src" / "features.py").exists():
        pytest.fail("src/features.py is missing. src/imbalance.py builds on your Week 5 pipeline.")
    if not SCRIPT.exists():
        pytest.fail("src/imbalance.py is missing. It is in lab_week06.zip.")
    r = subprocess.run([sys.executable, "src/imbalance.py"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.fail(f"src/imbalance.py exited {r.returncode}\n{(r.stdout + r.stderr)[-2000:]}")
    return json.loads(REPORT.read_text())


def test_imbalance_runs_and_writes_its_report(report):
    for key in ("base_rate", "baselines", "unadjusted", "class_weight_balanced", "matching_threshold"):
        assert key in report, f"outputs/imbalance.json has no {key}. Did you change main()?"


def test_both_baselines_are_priced(report):
    majority, rule = report["baselines"]["majority"], report["baselines"]["rule"]
    assert majority["flagged"] == 0, "the majority baseline should flag no order at all"
    assert 0 < rule["flagged"] < report["orders"], (
        "the rule should flag some orders and not others. A rule that flags everything or "
        "nothing is the majority baseline again.")
    assert rule["description"].strip(), "say in RULE, in words, what your rule flags"


def test_a_threshold_free_and_a_threshold_dependent_metric(report):
    u = report["unadjusted"]
    assert 0.5 < u["roc_auc"] < 0.9, f"ROC-AUC is {u['roc_auc']}. Did you keep column 1 of predict_proba?"
    assert u["pr_auc"] > 0, "PR-AUC is missing"
    for part in (u["at_0.5"], report["class_weight_balanced"]["at_0.5"]):
        assert {"precision", "recall"} <= set(part), "precision and recall at 0.5 are missing"


def test_the_matching_threshold_matches(report):
    m = report["matching_threshold"]
    w = report["class_weight_balanced"]["at_0.5"]
    assert m["threshold"] < 0.5, (
        "the matching threshold is 0.5, so the loop stopped at once. pred should be True where "
        "proba is at least t, and proba should be the unadjusted model's.")
    assert m["threshold"] > 0, (
        "the matching threshold is 0, so the loop never matched. Is pred proba >= t?")
    assert m["recall"] >= w["recall"], (
        f"at {m['threshold']} the unadjusted model finds {m['recall']} of the returns, short of "
        f"the class-weighted model's {w['recall']}")
    assert m["tp"] + m["fp"] + m["fn"] + m["tn"] == report["orders"], (
        "the four counts should add up to the number of orders")


def test_imbalance_is_seeded():
    """The same script twice gives the same file, because every shuffle has a seed."""
    if not REPORT.exists():
        pytest.fail("run src/imbalance.py first")
    first = REPORT.read_bytes()
    subprocess.run([sys.executable, "src/imbalance.py"], cwd=ROOT, capture_output=True, text=True)
    assert REPORT.read_bytes() == first, "two runs of src/imbalance.py gave different reports"


def test_milestone2_note_has_its_six_parts():
    if not NOTE.exists():
        pytest.fail("docs/milestone2_preprocessing.md does not exist yet. Start from "
                    "docs/milestone2_template.md.")
    text = NOTE.read_text()
    headings = re.findall(r"^##\s+\d", text, flags=re.M)
    assert len(headings) >= 6, f"the note has {len(headings)} numbered parts, and six are asked for"
    words = len(re.sub(r"<!--.*?-->", "", text, flags=re.S).split())
    assert words >= 600, (
        f"the note has {words} words outside the template's comments. Two to four pages is "
        "about 1,000 to 2,000.")
