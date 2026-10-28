import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "outputs" / "orders_clean.csv"
if not CLEAN.exists():
    raise SystemExit("outputs/orders_clean.csv is missing. Run make clean-data first.")
orders = pd.read_csv(CLEAN)
NUM = ["item_price", "discount_pct", "customer_prior_orders"]
CAT = ["channel", "category", "payment_method"]
# My cleaning keeps the four zero prices as blanks rather than guessing them, and a
# logistic regression cannot read a blank. The leak lab measures where a fit belongs,
# so it leaves those orders out rather than add an imputer, which would be a third
# thing fitted somewhere. Counted and printed, so nobody has to guess.
before = len(orders)
orders = orders.dropna(subset=NUM).reset_index(drop=True)
LEFT_OUT = before - len(orders)
# Which categories exist is known before any order arrives and says nothing about
# returns, so fitting the encoder on every order leaks nothing. Both arms share it.
onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(orders[CAT])
SEEDS = range(40)


def split(df, seed):
    """One train/test split per seed, stratified on returned, a quarter held out."""
    return train_test_split(df, test_size=0.25, random_state=seed,
                            stratify=df["returned"])


def score(train, test, scaler=None):
    """ROC-AUC of a logistic regression trained on train and scored on test.

    With no scaler given, the scaler is fitted on the training rows only, which is
    the honest arm. Passing one fitted elsewhere is the other arm.
    """
    if scaler is None:
        scaler = StandardScaler().fit(train[NUM])
    def features(df):
        return np.hstack([scaler.transform(df[NUM]), onehot.transform(df[CAT])])
    model = LogisticRegression(max_iter=2000).fit(features(train), train["returned"])
    return roc_auc_score(test["returned"], model.predict_proba(features(test))[:, 1])


def drop_outliers(df, reference):
    """Drop orders more than three sd from the mean order value of reference.

    The mean and sd are learned from reference, so which rows decide the rule and
    which rows lose orders can be chosen separately.
    """
    mu, sd = reference["order_value"].mean(), reference["order_value"].std()
    return df[((df["order_value"] - mu) / sd).abs() <= 3]


def r(x, places=4):
    """Round to a plain Python float, so two runs write identical bytes to the JSON."""
    return round(float(x), places)


def where_the_scaler_is_fitted():
    """The scaler fitted on the training rows, or on every order before the split."""
    everything = StandardScaler().fit(orders[NUM])
    result = {}
    for n in (40, 80, 200, 500, 1000, None):              # None is every training row
        on_train, on_all = [], []
        for seed in SEEDS:
            train, test = split(orders, seed)
            if n is not None:
                train = train.sample(min(n, len(train)), random_state=seed)
            on_train.append(score(train, test))
            on_all.append(score(train, test, everything))
        gap = np.array(on_all) - np.array(on_train)
        result[str(len(train))] = {"fitted_on_train": r(np.mean(on_train)),
                                   "fitted_on_all": r(np.mean(on_all)),
                                   "gap": r(gap.mean(), 5), "gap_sd": r(gap.std(), 5)}
        print(f"   {len(train):10,d}   {np.mean(on_train):.4f}     {np.mean(on_all):.4f}"
              f"     {gap.mean():+.5f}    {gap.std():.5f}")
    return result


def where_outliers_are_removed():
    """Outliers decided on the training rows and dropped from them only, or decided
    on every order and dropped from both sides of the split.

    Both arms of a seed share one split. The third number scores the honest model
    on the test set the flattering arm cleaned, to show whether the gap comes from
    the model or from the easier test set.
    """
    honest, flattering, honest_on_cleaned = [], [], []
    honest_rows, flattering_rows = [], []
    for seed in SEEDS:
        train, test = split(orders, seed)
        # honest. Decide on the training rows, and score every test order.
        h_train, h_test = drop_outliers(train, train), test
        honest.append(score(h_train, h_test))
        honest_rows.append(len(h_test))
        # flattering. Decide on all the orders, and drop from both sides.
        f_train, f_test = drop_outliers(train, orders), drop_outliers(test, orders)
        flattering.append(score(f_train, f_test))
        flattering_rows.append(len(f_test))
        # the honest model, scored on the test set the flattering arm cleaned
        honest_on_cleaned.append(score(h_train, f_test))
    honest, flattering = np.array(honest), np.array(flattering)
    honest_on_cleaned = np.array(honest_on_cleaned)
    gap = flattering - honest
    from_test_set = honest_on_cleaned - honest
    higher = int((gap > 0).sum())
    print(f"   honest      {honest.mean():.4f} sd {honest.std():.4f}    "
          f"{np.mean(honest_rows):g} test rows")
    print(f"   flattering  {flattering.mean():.4f} sd {flattering.std():.4f}    "
          f"{np.mean(flattering_rows):g} test rows on average")
    print(f"   gap         {gap.mean():+.4f} sd {gap.std():.4f}    "
          f"flattering higher in {higher} of {len(SEEDS)} seeds")
    print(f"   the honest model on the cleaned test set scores {honest_on_cleaned.mean():.4f}, "
          f"so {from_test_set.mean():+.4f} of the gap is the test set")
    return {"honest": r(honest.mean()), "honest_sd": r(honest.std()),
            "honest_test_rows": r(np.mean(honest_rows), 1),
            "flattering": r(flattering.mean()), "flattering_sd": r(flattering.std()),
            "flattering_test_rows": r(np.mean(flattering_rows), 1),
            "gap": r(gap.mean(), 5), "gap_sd": r(gap.std(), 5),
            "flattering_higher_in": higher,
            "honest_on_cleaned_test": r(honest_on_cleaned.mean()),
            "honest_on_cleaned_test_sd": r(honest_on_cleaned.std()),
            "gap_from_test_set": r(from_test_set.mean(), 5),
            "gap_from_test_set_sd": r(from_test_set.std(), 5)}


def main():
    print(f"{len(orders)} cleaned orders, {len(SEEDS)} seeds, every comparison paired")
    print(f"{LEFT_OUT} orders left out because a feature is blank\n")
    print("1. the scaler fitted on the training rows, or on every order before the split")
    print("   train rows   on train   on all     mean gap   sd of gap")
    scaler = where_the_scaler_is_fitted()
    print("\n2. outliers removed from the training rows only, or from both sides")
    outliers = where_outliers_are_removed()
    report = {"rows": len(orders), "rows_left_out_blank_feature": LEFT_OUT,
              "seeds": len(SEEDS), "features": NUM + CAT,
              "scaler_fitted_on_everything": scaler,
              "outliers_removed_before_the_split": outliers}
    (ROOT / "outputs" / "leak_lab.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()