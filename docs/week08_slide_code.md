# Week 8, the code on Friday's slides

This file holds every code box from the Friday slides, in slide order, to copy from, because copying out of the PDF loses the indentation that Python needs. Each box matches its slide, and where a slide leaves out a docstring to fit, the docstring appears here. The four lines that you write are shown as they arrive, marked TODO or FIX.

## Bringing the lab in, slide 2

```bash
cp -R lab_week08/. lab_week01/
cd lab_week01
source .venv/bin/activate      # Windows: .venv\Scripts\activate
make test
make evaluate
git add -A
git commit -m "Add the Week 8 lab"
```

## The top of src/evaluate.py, slide 4

```python
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
```

## Your pipeline, two alternatives and your rule, slide 5

```python
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
```

## Task A1. folds, and its FIX, slide 6

```python
def folds(y):
    """The 25 folds every candidate meets, 5 stratified folds shuffled 5 times."""
    out = []
    for seed in SEEDS:
        cv = StratifiedKFold(5, shuffle=True, random_state=0)   # FIX, shuffle with seed
        for k, (train, test) in enumerate(cv.split(np.zeros(len(y)), y)):
            out.append((seed, k, train, test))
    return out
```

## Task A2. fold_rows, and the floor, slide 7

```python
def fold_rows(orders, X, y):
    """One row for every fold and candidate, with ROC-AUC, PR-AUC and PR-AUC's floor."""
    rule = rule_scores(orders)
    models = candidates()
    rows = []
    for seed, k, train, test in folds(y):
        floor = None   # TODO, the share of returned orders in this test fold
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
```

## Task A3. paired, the differences and the wins, slide 8

```python
def paired(rows, against="your pipeline"):
    """Every other candidate minus your pipeline, ROC-AUC on the same fold."""
    wide = rows.pivot_table(index=["seed", "fold"], columns="candidate", values="roc_auc")
    out = {}
    for name in wide.columns:
        if name == against:
            continue
        a, b = wide[name].to_numpy(), wide[against].to_numpy()   # 25 scores each
        diffs = None   # TODO, fold by fold, this candidate minus your pipeline
        wins = None   # TODO, in how many folds this candidate is higher
        if diffs is None or wins is None:
            sys.exit("Fill in the two TODO lines in paired() first.")
        if np.ndim(wins) != 0:
            sys.exit("wins should be one number, the count. Add up the True values with .sum().")
        out[name] = {"difference": r4(np.mean(diffs)), "sd": r4(np.std(diffs)),
                     "wins": int(wins), "folds": len(diffs)}
    return out
```

## Running the evaluation, slide 9

```bash
make evaluate
python -m pytest -q tests/test_week8_contract.py
git add src/evaluate.py
git commit -m "Fill in src/evaluate.py: 25 folds, the floor, the paired differences"
```

## Starting the note, slide 11

```bash
cp docs/evaluation_template.md docs/evaluation_note.md
```

## Handing in, slide 14

```bash
git status
git log --oneline
cd ..
zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell
```
