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


def date_features(df):
    """Six numbers mined from order_date, each from the order's own date alone.

    Nothing here looks at another row or at the answer, so nothing needs to be
    fitted inside a fold. The day count starts from DAY_ZERO, a fixed day, rather
    than the earliest date in the table, so that adding or removing other orders
    never changes this order's value. Returns a new frame and leaves df alone.
    """
    d = pd.to_datetime(df["order_date"])
    out = pd.DataFrame({
        "day_of_week": d.dt.dayofweek,
        "month": d.dt.month,
        "day_of_month": d.dt.day,
        "is_weekend": (d.dt.dayofweek >= 5).astype(int),
        "week_of_year": d.dt.isocalendar().week.astype(int),
        "days_since_2025": (d - DAY_ZERO).dt.days,
    }, index=df.index)
    return out[DATE_FEATURES]


def orders_in_2025(df):
    """The date feature that would leak. Kept to show it was rejected, never called.

    It counts every order the customer placed in 2025, including orders placed
    after this one. On the day of the prediction those orders had not happened.
    customer_prior_orders counts only the earlier ones and is the honest version.
    """
    return df.groupby("customer_id")["order_id"].transform("count")


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