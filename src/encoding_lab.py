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


def correlations(orders):
    """How close each version of the customer rate is to the order's own label.

    The group mean sees every label, the order's own included. TargetEncoder 
    fitted and then used to transform the same rows smooths the rates
    but still lets each order see its own label. fit_transform
    cross-fits, so each order's rate comes from the other folds only.
    """
    y = orders[TARGET]
    customer = orders[["customer_id"]]
    versions = {
        "group_mean_on_every_order": leaked_customer_rate(orders),
        "target_encoder_fit_then_transform":
            TargetEncoder(target_type="binary", random_state=0)
            .fit(customer, y).transform(customer)[:, 0],
        "target_encoder_fit_transform":
            TargetEncoder(target_type="binary", random_state=0)
            .fit_transform(customer, y)[:, 0],
    }
    result = {}
    print("correlation with the order's own label")
    for name, col in versions.items():
        result[name] = round(float(np.corrcoef(col, y)[0, 1]), 4)
        print(f"  {name:34s} {result[name]:.4f}")
    return result


def rows_per_level(orders):
    """Values and orders per value of every categorical column, customer_id included.

    The number to print before choosing an encoding: a target rate estimated
    from two orders is mostly the label of those two orders.
    """
    result = {}
    for col in CATEGORICAL + ["customer_id"]:
        values = int(orders[col].nunique())
        result[col] = {"values": values,
                       "orders_per_value": round(float(len(orders) / values), 1)}
    print("rows per level")
    for col, v in sorted(result.items(), key=lambda kv: kv[1]["values"]):
        print(f"  {col:16s} {v['values']:4d} values {v['orders_per_value']:8.1f} orders each")
    return result


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