"""
src/operating_point.py

Week 8 homework, section 4 of the evaluation note. Milestone 2 reported the
operating point, a threshold of 0.194, as one precision and one recall with no
spread. This reports it again the Week 8 way: on the same 25 folds as
src/evaluate.py, with a mean and an sd, and fold by fold against the rule.

    python src/operating_point.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluate import folds, r4, rule_scores, spread  # noqa: E402
from features import TARGET, build_pipeline, feature_frame  # noqa: E402

THRESHOLD = 0.194   # the Milestone 2 operating point, from outputs/imbalance.json


def main():
    orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
    y = orders[TARGET].to_numpy()
    X = feature_frame(orders)
    rule = rule_scores(orders)
    rows = []
    for seed, k, train, test in folds(y):
        p = clone(build_pipeline()).fit(X.iloc[train], y[train]).predict_proba(X.iloc[test])[:, 1]
        flagged = p >= THRESHOLD
        rows.append({"model_precision": precision_score(y[test], flagged),
                     "model_recall": recall_score(y[test], flagged),
                     "model_flagged": int(flagged.sum()),
                     "rule_precision": precision_score(y[test], rule[test]),
                     "rule_recall": recall_score(y[test], rule[test]),
                     "rule_flagged": int(rule[test].sum())})
    rows = pd.DataFrame(rows)
    report = {"threshold": THRESHOLD, "folds": len(rows)}
    for col in rows.columns:
        report[col] = spread(rows[col])
    for score in ("precision", "recall"):
        diffs = (rows[f"model_{score}"] - rows[f"rule_{score}"]).to_numpy()
        report[f"{score}_model_minus_rule"] = {"difference": r4(np.mean(diffs)), "sd": r4(np.std(diffs)),
                                               "model_higher_in": int((diffs > 0).sum())}
    print(json.dumps(report, indent=2))
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "operating_point.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()