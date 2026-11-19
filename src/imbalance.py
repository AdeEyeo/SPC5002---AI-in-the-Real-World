"""
src/imbalance.py

Week 6 assignment, Part A. Thursday's Tasks 1, 3 and 4 on your own pipeline.

Fill in the four lines marked TODO, then run make imbalance, or
python src/imbalance.py. It writes outputs/imbalance.json, which your
Milestone 2 note quotes in its part 4.

Everything else in this file is given. It imports build_pipeline,
feature_frame and TARGET from your own src/features.py.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import TARGET, build_pipeline, feature_frame  # noqa: E402

# Your one-line rule, in words, for the report. Change it if your rule is different.
RULE = "flag every footwear or apparel order"


def baselines(orders):
    """Two predictions that need no model, as columns of 0 and 1."""
    majority = np.zeros(len(orders), dtype=int)   # TODO, a 0 for every order
    rule = orders["category"].isin(["footwear", "apparel"]).astype(int)   # TODO, your one-line rule as 0 and 1, the one RULE describes
    return majority, rule


def oof_proba(model, X, y):
    """Out-of-fold probability of a return for every order, averaged over 5 shuffles."""
    runs = []
    for seed in range(5):
        cv = StratifiedKFold(5, shuffle=True, random_state=seed)
        p = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]   # TODO, as on Thursday, cross_val_predict and column 1
        if p is None:
            sys.exit("Fill in the TODO line in oof_proba() first.")
        runs.append(p)
    return np.mean(runs, axis=0)


def matching_threshold(proba, y, target):
    """The highest threshold at which proba finds at least target of the returns."""
    for t in np.arange(0.5, 0, -0.001):
        pred = proba >= t   # TODO, True where proba is at least t
        if pred is None:
            sys.exit("Fill in the TODO line in matching_threshold() first.")
        if recall_score(y, pred) >= target:
            return round(float(t), 3)
    return 0.0


def with_class_weight(pipe):
    """The same pipeline with class_weight="balanced" on its last step, whatever it is called."""
    last = pipe.steps[-1][0]
    return pipe.set_params(**{f"{last}__class_weight": "balanced"})


def at(y, pred):
    """What a yes or no prediction gets right, with the four counts."""
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return {"accuracy": round(accuracy_score(y, pred), 4),
            "precision": round(precision_score(y, pred, zero_division=0), 4),
            "recall": round(recall_score(y, pred), 4),
            "f1": round(f1_score(y, pred), 4),
            "flagged": int(np.sum(pred)), "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}


def ranking(y, proba):
    """Threshold-free scores, which read only the order of the probabilities."""
    return {"roc_auc": round(roc_auc_score(y, proba), 4),
            "pr_auc": round(average_precision_score(y, proba), 4)}


def main():
    orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
    y = orders[TARGET].to_numpy()
    X = feature_frame(orders)

    majority, rule = baselines(orders)
    if majority is None or rule is None:
        sys.exit("Fill in the two TODO lines in baselines() first.")
    proba = oof_proba(build_pipeline(), X, y)
    proba_w = oof_proba(with_class_weight(build_pipeline()), X, y)
    target = recall_score(y, proba_w >= 0.5)
    t = matching_threshold(proba, y, target)

    report = {
        "orders": len(orders),
        "base_rate": round(float(y.mean()), 4),
        "baselines": {"majority": at(y, majority), "rule": {"description": RULE, **at(y, rule)}},
        "unadjusted": {**ranking(y, proba), "highest_probability": round(float(proba.max()), 4),
                       "at_0.5": at(y, proba >= 0.5)},
        "class_weight_balanced": {**ranking(y, proba_w), "at_0.5": at(y, proba_w >= 0.5)},
        "matching_threshold": {"threshold": t, **at(y, proba >= t)},
    }
    for name, part in [("majority", report["baselines"]["majority"]), ("rule", report["baselines"]["rule"]),
                       ("unadjusted at 0.5", report["unadjusted"]["at_0.5"]),
                       ("weighted at 0.5", report["class_weight_balanced"]["at_0.5"]),
                       (f"unadjusted at {t}", report["matching_threshold"])]:
        print(f"{name:20s} precision {part['precision']:.3f}  recall {part['recall']:.3f}  "
              f"flagged {part['flagged']:4d}  TP {part['tp']:3d}  FN {part['fn']:3d}")
    print(f"ROC-AUC {report['unadjusted']['roc_auc']}, highest probability "
          f"{report['unadjusted']['highest_probability']}, matching threshold {t}, "
          f"base rate {report['base_rate']}")
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "imbalance.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
