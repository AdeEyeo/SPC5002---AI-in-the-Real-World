"""
src/evaluate.py

Week 8, an evaluation you can defend for your own pipeline.

Fill in the four lines marked TODO or FIX and run make evaluate, or
python src/evaluate.py, which scores your pipeline, two alternatives and your
Week 6 rule on the same 25 folds, 5 folds shuffled 5 times. The script writes
outputs/evaluation.json, in which every score stands beside its spread, PR-AUC
beside its floor, and each alternative is compared with your pipeline fold by
fold, and it writes the scores of every fold to outputs/evaluation_folds.csv.
Your evaluation note quotes both files.

Everything else in this file is given, and the file imports build_pipeline,
feature_frame and TARGET from your own src/features.py.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import TARGET, build_pipeline, feature_frame  # noqa: E402

# Your Week 6 rule, in words. Change it, and rule_scores, if yours is different.
RULE = "flag every footwear or apparel order"
SEEDS = range(5)


def rule_scores(orders):
    """Your Week 6 rule as a score, 1 for a flagged order and 0 for the rest."""
    return orders["category"].isin(["footwear", "apparel"]).astype(int).to_numpy()


def with_class_weight(pipe):
    """The same pipeline with class_weight="balanced" on its last step, as in Week 6."""
    last = pipe.steps[-1][0]
    return pipe.set_params(**{f"{last}__class_weight": "balanced"})


def with_model(pipe, model):
    """The same pipeline with its last step swapped for model, whatever the step is called."""
    last = pipe.steps[-1][0]
    return pipe.set_params(**{last: model})


def candidates():
    """Your pipeline first, then the two alternatives it is compared with."""
    return {
        "your pipeline": build_pipeline(),
        "class_weight balanced": with_class_weight(build_pipeline()),
        "decision tree, depth 4": with_model(build_pipeline(),
                                             DecisionTreeClassifier(max_depth=4, random_state=0)),
    }


def folds(y):
    """The 25 folds every candidate meets, 5 stratified folds shuffled 5 times."""
    out = []
    for seed in SEEDS:
        cv = StratifiedKFold(5, shuffle=True, random_state=seed)   # FIX, shuffle with seed
        for k, (train, test) in enumerate(cv.split(np.zeros(len(y)), y)):
            out.append((seed, k, train, test))
    return out


def fold_rows(orders, X, y):
    """One row for every fold and candidate, with ROC-AUC, PR-AUC and PR-AUC's floor."""
    rule = rule_scores(orders)
    models = candidates()
    rows = []
    for seed, k, train, test in folds(y):
        floor = y[test].mean()   # TODO, the share of returned orders in this test fold
        if floor is None:
            sys.exit("Fill in the TODO line for floor in fold_rows() first.")
        scores = {"the rule": rule[test]}
        for name, pipe in models.items():
            fitted = clone(pipe).fit(X.iloc[train], y[train])
            scores[name] = fitted.predict_proba(X.iloc[test])[:, 1]
        for name, p in scores.items():
            rows.append({"seed": seed, "fold": k, "candidate": name, "floor": floor,
                         "roc_auc": roc_auc_score(y[test], p),
                         "pr_auc": average_precision_score(y[test], p)})
    return pd.DataFrame(rows)


def summary(rows):
    """The mean and sd over the 25 folds for every candidate, and PR-AUC's floor and lift."""
    out = {}
    for name, g in rows.groupby("candidate", sort=False):
        lift = g["pr_auc"] / g["floor"]
        out[name] = {"roc_auc": spread(g["roc_auc"]), "pr_auc": spread(g["pr_auc"]),
                     "floor": r4(g["floor"].mean()), "lift": spread(lift)}
    return out


def paired(rows, against="your pipeline"):
    """Every other candidate minus your pipeline, ROC-AUC on the same fold."""
    wide = rows.pivot_table(index=["seed", "fold"], columns="candidate", values="roc_auc")
    out = {}
    for name in wide.columns:
        if name == against:
            continue
        a, b = wide[name].to_numpy(), wide[against].to_numpy()   # 25 scores each
        diffs = a - b   # TODO, fold by fold, this candidate minus your pipeline
        wins = int((diffs > 0).sum())   # TODO, in how many folds this candidate is higher
        if diffs is None or wins is None:
            sys.exit("Fill in the two TODO lines in paired() first.")
        if np.ndim(wins) != 0:
            sys.exit("wins should be one number, the count. Add up the True values with .sum().")
        out[name] = {"difference": r4(np.mean(diffs)), "sd": r4(np.std(diffs)),
                     "wins": int(wins), "folds": len(diffs)}
    return out


def spread(values):
    return {"mean": r4(np.mean(values)), "sd": r4(np.std(values))}


def r4(x):
    """A plain float rounded to four places, and never -0.0, so two runs write the same bytes."""
    return round(float(x), 4) + 0.0


def main():
    orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
    y = orders[TARGET].to_numpy()
    X = feature_frame(orders)
    rows = fold_rows(orders, X, y)
    report = {
        "orders": len(orders),
        "base_rate": r4(y.mean()),
        "folds": "5 stratified folds, shuffled with seeds 0 to 4, 25 in all",
        "rule": RULE,
        "candidates": summary(rows),
        "paired_with_your_pipeline": paired(rows),
    }
    print(f"{'':24s} {'ROC-AUC':>8s} {'sd':>7s}   {'PR-AUC':>7s} {'floor':>7s} {'lift':>6s}")
    for name, c in report["candidates"].items():
        print(f"{name:24s} {c['roc_auc']['mean']:8.4f} {c['roc_auc']['sd']:7.4f}   "
              f"{c['pr_auc']['mean']:7.4f} {c['floor']:7.4f} {c['lift']['mean']:6.2f}")
    print("paired with your pipeline, ROC-AUC on the same 25 folds")
    for name, p in report["paired_with_your_pipeline"].items():
        print(f"{name:24s} {p['difference']:+8.4f}  sd {p['sd']:.4f}  higher in {p['wins']:2d} of {p['folds']}")
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")
    rows.round(4).to_csv(ROOT / "outputs" / "evaluation_folds.csv", index=False)


if __name__ == "__main__":
    main()
