# Week 5, the code on Friday's slides

Every code box on the Friday slides, in slide order, to copy from. Copying out
of the PDF loses the indentation, and Python needs it. Where a slide leaves a
docstring out to fit, it is here. This file is written by the same script that
builds the slides, so the two always match.

## Bringing the lab in, slide 2

```bash
cp -R lab_week05/. lab_week01/
cd lab_week01
source .venv/bin/activate      # Windows: .venv\Scripts\activate
make clean-data
cp outputs/orders_clean.csv data/
make test
git add -A
git commit -m "Add the Week 5 lab and my cleaned table in data/"
jupyter lab
```

## The top of src/features.py, slide 4

```python
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (StratifiedGroupKFold, StratifiedKFold,
                                     cross_val_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder

ROOT = Path(__file__).resolve().parents[1]
TARGET = "returned"

NUMERIC = ["item_price", "discount_pct", "customer_prior_orders",
           "delivery_days", "order_value", "quantity"]
CATEGORICAL = ["channel", "category", "payment_method", "customer_region"]
DATE_FEATURES = ["day_of_week", "month", "day_of_month", "is_weekend",
                 "week_of_year", "days_since_2025"]
HIGH_CARDINALITY = ["customer_id"]

# a fixed day, not the earliest date in the table, so that a row's value depends
# on that row alone. The data starts on this day, so the numbers are the same.
DAY_ZERO = pd.Timestamp("2025-01-01")
```

## One pipeline holds every step that learns, slide 5

```python
def build_pipeline(numeric=None, categorical=None, target_encode=None):
    """Every step that learns a number, in one object, ending in the model.

    The imputer learns a median, the scaler a mean and an sd, the one-hot encoder
    the list of categories, and the target encoder a rate per customer. Fitted
    inside cross-validation, each learns from the training folds only.
    handle_unknown="ignore" lets a category never seen in training contribute
    nothing, rather than raise an error that tempts you to fit on every row.

    The six date features are left out by default, because Thursday measured them
    and they cost a little. Pass numeric=NUMERIC + DATE_FEATURES to use them.
    """
    numeric = NUMERIC if numeric is None else numeric
    categorical = CATEGORICAL if categorical is None else categorical
    parts = [
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ]
    if target_encode:
        encoder = TargetEncoder(target_type="binary", random_state=0)
        parts.append(("target", encoder, target_encode))
    return Pipeline([("features", ColumnTransformer(parts)),
                     ("model", LogisticRegression(max_iter=2000))])
```

## feature_frame hands over raw columns, and cv_auc scores them, slide 6

```python
def feature_frame(df):
    """The columns handed to cross-validation. Raw, nothing fitted.

    The numbers, the four categories, customer_id for a target encoding inside the
    pipeline, and the six date features. Every value comes from its own row, so
    nothing here needs to be inside a fold. The answer, order_id and the date
    string are left out.
    """
    raw = df[NUMERIC + CATEGORICAL + HIGH_CARDINALITY]
    return pd.concat([raw, date_features(df)], axis=1)


def cv_auc(model, X, y, groups=None, repeats=5):
    """ROC-AUC over 5 folds, repeated, as a mean and an sd. groups keeps each
    group's rows on one side of every split."""
    scores = []
    for r in range(repeats):
        cv = (StratifiedKFold(5, shuffle=True, random_state=r) if groups is None
              else StratifiedGroupKFold(5, shuffle=True, random_state=r))
        scores += list(cross_val_score(model, X, y, cv=cv, groups=groups,
                                       scoring="roc_auc"))
    return {"mean": round(float(np.mean(scores)), 4),
            "sd": round(float(np.std(scores)), 4)}
```

## main fits once, then scores with and without the dates, slide 7

```python
def main():
    orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
    y = orders[TARGET]
    X = feature_frame(orders)
    fitted = build_pipeline().fit(X, y)
    width = fitted.named_steps["features"].transform(X.head()).shape[1]
    print(f"{len(X)} orders, {X.shape[1]} columns in, {width} features out")
    without = cv_auc(build_pipeline(), X, y)
    with_dates = cv_auc(build_pipeline(numeric=NUMERIC + DATE_FEATURES), X, y)
    print(f"without the date features  {without['mean']:.4f}  sd {without['sd']:.4f}")
    print(f"with the six date features {with_dates['mean']:.4f}  sd {with_dates['sd']:.4f}")
    report = {"orders": len(X), "columns_in": list(X.columns), "features_out": int(width),
              "auc_without_date_features": without, "auc_with_date_features": with_dates}
    (ROOT / "outputs").mkdir(exist_ok=True)
    text = json.dumps(report, indent=2) + "\n"
    (ROOT / "outputs" / "features.json").write_text(text)


if __name__ == "__main__":
    main()
```

## The one that would leak, written and never called, slide 9

```python
def orders_in_2025(df):
    """The date feature that would leak. Kept to show it was rejected, never called.

    It counts every order the customer placed in 2025, including orders placed
    after this one. On the day of the prediction those orders had not happened.
    customer_prior_orders counts only the earlier ones and is the honest version.
    """
    return df.groupby("customer_id")["order_id"].transform("count")
```

## Running the features, slide 10

```bash
make features
python -m pytest -q tests/test_week5_contract.py
git add src/features.py
git commit -m "Write src/features.py: one pipeline, six date features, one rejected"
```

## The top of src/encoding_lab.py, slide 12

```python
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import TargetEncoder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from features import (CATEGORICAL, NUMERIC, TARGET,  # noqa: E402
                      build_pipeline, cv_auc, feature_frame)


def leaked_customer_rate(df):
    """Each customer's return rate over every order, the order's own label included.

    The mistake, made on purpose so that it can be measured. For a customer with
    one order the rate is the label. Any split made afterwards, grouped or not,
    starts from a column that already holds the answer.
    """
    return df.groupby("customer_id")[TARGET].transform("mean")
```

## score_routes, written out, slide 13

```python
def score_routes(orders):
    """Three ways to give the model a customer's return rate, each scored twice.

    Once with a random split and once with the split grouped by customer, so that
    no customer is in training and test at once. Every score comes with its sd.
    """
    y = orders[TARGET]
    customers = orders["customer_id"]
    X = feature_frame(orders)
    X_leak = X.assign(customer_rate=leaked_customer_rate(orders))
    routes = {
        "one_hot_only":
            (build_pipeline(), X),
        "target_encoded_in_the_pipeline":
            (build_pipeline(target_encode=["customer_id"]), X),
        "customer_rate_on_every_order":
            (build_pipeline(numeric=NUMERIC + ["customer_rate"]), X_leak),
    }
    scores = {}
    for name, (model, frame) in routes.items():
        scores[name] = {
            "random_split": cv_auc(model, frame, y),
            "grouped_by_customer": cv_auc(model, frame, y, groups=customers)}
        r, g = scores[name]["random_split"], scores[name]["grouped_by_customer"]
        print(f"{name:32s} random {r['mean']:.4f} sd {r['sd']:.4f}   "
              f"grouped {g['mean']:.4f} sd {g['sd']:.4f}")
    return scores
```

## main of src/encoding_lab.py, slide 14

```python
def main():
    orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
    report = {"scores": score_routes(orders),
              "correlation_with_own_label": correlations(orders),
              "rows_per_level": rows_per_level(orders)}
    (ROOT / "outputs").mkdir(exist_ok=True)
    text = json.dumps(report, indent=2) + "\n"
    (ROOT / "outputs" / "encoding_lab.json").write_text(text)


if __name__ == "__main__":
    main()
```

## Running the encoding lab, slide 15

```bash
make encoding-lab
git add src/encoding_lab.py
git commit -m "Measure three encodings of the customer, random and grouped, each with its sd"
```

## Handing in, slide 19

```bash
git status
git log --oneline
cd ..
zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell
```
