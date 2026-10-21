# Week 4, the code on Friday's slides

Every code box on the Friday slides, in slide order, to copy from. Copying out
of the PDF loses the indentation, and Python needs it. This file is written by
the same script that builds the slides, so the two always match.

## Bringing the lab in, slide 3

```bash
cp -R lab_week04/. lab_week01/
cd lab_week01
source .venv/bin/activate      # Windows: .venv\Scripts\activate
ls data                        # orders_joined.csv must be listed
make setup
make test
git add -A
git commit -m "Add the Week 4 lab: brief, homework and eight tests"
jupyter lab
```

## The top of src/cleaning.py, with the ledger, slide 6

```python
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
JOINED = ROOT / "data" / "orders_joined.csv"
OUT = ROOT / "outputs"

class Ledger:
    """One line per cleaning step, so every order that leaves has a reason."""
    def __init__(self):
        self.steps = []
    def record(self, step, before, after, reason):
        self.steps.append({"step": step, "before": before, "after": after,
                           "removed": before - after, "reason": reason})
    def total_removed(self):
        return sum(s["removed"] for s in self.steps)
    def to_frame(self):
        return pd.DataFrame(self.steps,
                            columns=["step", "before", "after", "removed", "reason"])
```

## One step, slide 7

```python
def drop_impossible_quantities(df, led):
    """Remove orders for fewer than one item.

    An order row exists because something was bought. A quantity of zero is not a
    small order, it is a row that contradicts its own reason for existing, and
    there is no value that would make it right. Four rows.
    """
    out = df[df["quantity"] >= 1]
    led.record("drop_impossible_quantities", len(df), len(out),
               "an order of zero items contradicts the existence of the row")
    return out
```

## clean, slide 8

```python
def clean(df):
    """Apply every decision, in order, and return the frame with its ledger.

    The order matters only for the ledger. The four removals are on disjoint sets
    of rows, so the result is the same whichever order they run in, and the fact
    that 4 + 4 + 4 + 5 equals the 17 the audit found is how we know that.
    """
    led = Ledger()
    out = df
    for step in (drop_impossible_quantities,
                 drop_non_positive_prices,
                 drop_negative_order_values,
                 drop_sentinel_delivery_times):
        out = step(out, led)
    out = leave_marketing_opt_in_missing(out)
    return out.reset_index(drop=True), led
```

## main, slide 9

```python
def main():
    df = pd.read_csv(JOINED)
    out, led = clean(df)

    print(led.to_frame()[["step", "before", "after", "removed"]].to_string(index=False))
    assert len(df) - len(out) == led.total_removed(), "a row left without a reason"

    print(f"\n{len(df)} -> {len(out)}   {led.total_removed()} rows removed, all named")
    print(f"base rate {df.returned.mean():.4f} -> {out.returned.mean():.4f}")

    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / "orders_clean.csv", index=False, lineterminator="\n")
    led.to_frame().to_csv(OUT / "cleaning_ledger.csv", index=False, lineterminator="\n")


if __name__ == "__main__":
    main()
```

## Running the cleaning, slide 10

```bash
make clean-data
git add src/cleaning.py
git commit -m "Write src/cleaning.py: four named steps, a ledger and its assertion"
```

## The other defensible choice, slide 11

```python
def mark_sentinel_delivery_times(df, led):
    """The other defensible choice. Keep the orders, make the absence visible.

    Turns -999 into a genuine blank and keeps a flag, so nothing downstream can
    average it away. It removes nothing, so its ledger line says 0 removed and
    its reason says what changed. Use it in place of the drop in clean if you
    would rather keep the orders than the column. Not both. Not called below.
    """
    out = df.copy()
    sentinel = out["delivery_days"] == -999
    out["delivery_days"] = out["delivery_days"].astype(float).where(~sentinel)
    out["delivery_days_missing"] = out["delivery_days"].isna()
    led.record("mark_sentinel_delivery_times", len(df), len(out),
               f"kept and flagged {int(sentinel.sum())} orders, "
               "where -999 means not recorded")
    return out
```

## Task B, the numbers, slide 12

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

orders = pd.read_csv("../data/orders_joined.csv")
d = orders["delivery_days"]
real = d[d != -999]

for name, col in [("with the five", d), ("without them", real)]:
    print(f"{name:14s} mean {col.mean():6.3f}   sd {col.std():6.3f}   "
          f"z of 5 days {(5 - col.mean()) / col.std():+.4f}")
```

## Task B, the figure, slide 13

```python
fig, axes = plt.subplots(1, 2, figsize=(9, 3), sharey=True)
axes[0].hist((real - d.min()) / (d.max() - d.min()), bins=20, range=(0, 1))
axes[0].set_title("min-max fitted with the -999 rows in")
axes[1].hist((real - real.min()) / (real.max() - real.min()), bins=20, range=(0, 1))
axes[1].set_title("min-max fitted on the real values")
Path("../outputs").mkdir(exist_ok=True)
fig.savefig("../outputs/delivery_minmax.png", dpi=150, bbox_inches="tight")
```

## The top of src/leak_lab.py, slide 15

```python
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
# Which categories exist is known before any order arrives and says nothing about
# returns, so fitting the encoder on every order leaks nothing. Both arms share it.
onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(orders[CAT])
SEEDS = range(40)
# then split, score and drop_outliers, Thursday's cells, unchanged
```

## One measurement, slide 16

```python
def where_the_scaler_is_fitted():
    """The scaler fitted on the training rows, or on every order before the split."""
    everything = StandardScaler().fit(orders[NUM])
    result = {}
    for n in (40, 80, 200, 500, 1000, None):          # None is every training row
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
              f"     {gap.mean():+.5f}   {gap.std():.5f}")
    return result
```

## main, slide 17

```python
def main():
    print(f"{len(orders)} cleaned orders, {len(SEEDS)} seeds, every comparison paired\n")
    print("1. the scaler fitted on the training rows, or on every order before the split")
    print("   train rows   on train   on all     mean gap   sd of gap")
    scaler = where_the_scaler_is_fitted()
    print("\n2. outliers removed from the training rows only, or from both sides")
    outliers = where_outliers_are_removed()
    report = {"rows": len(orders), "seeds": len(SEEDS), "features": NUM + CAT,
              "scaler_fitted_on_everything": scaler,
              "outliers_removed_before_the_split": outliers}
    (ROOT / "outputs" / "leak_lab.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
```

## Running the leak lab, slide 18

```bash
make leak-lab
git add src/leak_lab.py
git commit -m "Measure where the scaler and outlier removal belong, paired over 40 seeds"
```

## Handing in, slide 22

```bash
git status
git log --oneline
cd ..
zip -r homework.zip lab_week01 -x "lab_week01/.venv/*"   # Mac, Linux, JupyterHub
tar -a -c -f homework.zip --exclude=.venv lab_week01      # Windows PowerShell
```
