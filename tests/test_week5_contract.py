"""
tests/test_week5_contract.py

Eight tests. You did not write them and you may not change them.

None asserts a score. The two that matter check that no input column was built
from the target, and that nothing which learns a number sits outside the pipeline.
The last one checks that the encoding lab reports its measurements with a spread.

    python -m pytest -q tests/test_week5_contract.py
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "src" / "features.py"
ENCODING_LAB = ROOT / "src" / "encoding_lab.py"
CLEAN = ROOT / "data" / "orders_clean.csv"
OUT = ROOT / "outputs"
TARGET = "returned"

# the largest correlation any honest feature reaches on this data is 0.0466.
# a group mean of the target reaches 0.6888. 0.5 is a long way from both.
MAX_HONEST_CORRELATION = 0.5


def _load():
    spec = importlib.util.spec_from_file_location("student_features", FEATURES)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["student_features"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def df():
    if not CLEAN.exists():
        pytest.fail(
            "data/orders_clean.csv is missing. Run make clean-data and then "
            "cp outputs/orders_clean.csv data/, or copy it from the "
            "week05_thursday folder. docs/week05_brief.md has both.")
    return pd.read_csv(CLEAN)


@pytest.fixture(scope="module")
def mod(df):
    if not FEATURES.exists():
        pytest.fail("src/features.py does not exist yet")
    return _load()


def test_features_module_exposes_the_two_names(mod):
    for name in ("build_pipeline", "feature_frame"):
        assert hasattr(mod, name), f"src/features.py must define {name}"


def test_build_pipeline_returns_a_pipeline(mod):
    from sklearn.pipeline import Pipeline
    assert isinstance(mod.build_pipeline(), Pipeline), (
        "build_pipeline() must return a scikit-learn Pipeline, not a fitted array"
    )


def test_no_input_column_is_built_from_the_target(mod, df):
    """
    The one that matters.

    Every column you hand to cross-validation gets its correlation with the target
    measured. A feature built from a row's own values cannot be strongly
    correlated with the answer on this data, and the largest honest one is 0.0466.

    A group mean of the target reaches 0.6888, because 305 customers placed
    exactly one order and for those rows the feature is the label.
    """
    X = mod.feature_frame(df)
    y = df[TARGET]
    offenders = []
    for col in X.columns:
        s = X[col]
        if not pd.api.types.is_numeric_dtype(s):
            continue
        s = s.fillna(s.median())
        if s.nunique() < 2:
            continue
        r = abs(float(np.corrcoef(s, y)[0, 1]))
        if r > MAX_HONEST_CORRELATION:
            offenders.append(f"{col} (|r| = {r:.4f})")
    assert not offenders, (
        "these input columns are too closely related to the answer:\n  "
        + "\n  ".join(offenders)
        + "\n\nA feature built from the target is the target until you can show "
          "when it was computed. Move it inside the pipeline."
    )


def test_the_target_is_not_among_the_features(mod, df):
    X = mod.feature_frame(df)
    assert TARGET not in X.columns, "returned is the answer, not a feature"
    for leftover in ("order_id", "export_seq"):
        assert leftover not in X.columns, f"{leftover} is not a feature"


def test_nothing_is_fitted_outside_the_pipeline():
    """
    A grep with opinions. A fit or fit_transform anywhere except main, or a group
    statistic of the target, is how a number learned from every row ends up in a
    column. main may fit the finished pipeline, and nothing else may fit at all.
    """
    if not FEATURES.exists():
        pytest.fail("src/features.py does not exist yet")
    src = FEATURES.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    in_main = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            in_main = {id(n) for n in ast.walk(node)}
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("fit", "fit_transform") and id(node) not in in_main:
                bad.append(f"line {node.lineno}: .{node.func.attr}(...) outside main")
            if node.func.attr == "groupby":
                window = "\n".join(lines[node.lineno - 1:node.lineno + 2])
                if TARGET in window or "TARGET" in window:
                    bad.append(f"line {node.lineno}: groupby touching {TARGET}")
    assert not bad, (
        "src/features.py builds something from the target:\n  "
        + "\n  ".join(bad)
        + "\n\nIf a step learns a number, it belongs inside build_pipeline(). "
          "If you want to measure the leaked version, do it in src/encoding_lab.py."
    )


def test_feature_frame_is_deterministic(mod, df):
    a = mod.feature_frame(df)
    b = mod.feature_frame(df)
    assert list(a.columns) == list(b.columns)
    pd.testing.assert_frame_equal(a, b)


def test_feature_frame_does_not_mutate_its_input(mod):
    """You will call it more than once. It has to leave the orders as it found them.

    A fresh read, because the shared table may already have been changed by an
    earlier test, and then a second change looks like no change.
    """
    fresh = pd.read_csv(CLEAN)
    before = fresh.copy()
    mod.feature_frame(fresh)
    added = sorted(set(fresh.columns) - set(before.columns))
    assert not added, (
        f"feature_frame added {added} to the frame it was given. Build a new "
        "frame and return it, and leave the orders as you found them.")
    pd.testing.assert_frame_equal(fresh, before)


def test_encoding_lab_reports_the_grouped_split_with_a_spread(df):
    """
    Task C. The encodings of customer_id, the grouped split and the rows per
    level, each score with its spread, in outputs/encoding_lab.json. The keys are
    yours. The test checks that the pieces are there, not that you used my words
    or found my numbers.
    """
    if not ENCODING_LAB.exists():
        pytest.fail("src/encoding_lab.py does not exist yet")
    r = subprocess.run([sys.executable, "src/encoding_lab.py"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"src/encoding_lab.py exited {r.returncode}\n{r.stderr[-2000:]}"
    path = OUT / "encoding_lab.json"
    assert path.exists(), "write outputs/encoding_lab.json"
    text = path.read_text()
    json.loads(text)
    text = text.lower()
    assert "group" in re.sub(r"group_?mean|groupby", "", text), (
        "the grouped split is missing, or never says group")
    assert "customer_id" in text, "the rows per level table needs customer_id in it"
    assert any(w in text for w in ("sd", "std", "spread", "stdev")), (
        "report a spread, the standard deviation over your folds, beside each "
        "score. A difference without its spread cannot be read.")
