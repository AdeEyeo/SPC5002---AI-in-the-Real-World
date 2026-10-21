from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"


def describe(col):
    info = {"type": str(col.dtype),
            "distinct": int(col.nunique()),
            "missing": int(col.isna().sum()),
            "constant": bool(col.nunique(dropna=False) == 1)}
    if pd.api.types.is_numeric_dtype(col) and not pd.api.types.is_bool_dtype(col):
        info["range"] = [col.min().item(), col.max().item()]
    else:
        counts = col.value_counts().rename(index=str)
        top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        info["top"] = {k: int(v) for k, v in top}
    return info


def profile(df):
    return {"rows": len(df),
            "columns": len(df.columns),
            "profile": {c: describe(df[c]) for c in df.columns}}


def main():
    orders = pd.read_csv(DATA / "orders_joined.csv")
    penguins = pd.read_csv(DATA / "penguins_raw.csv")
    report = {"orders": profile(orders), "penguins": profile(penguins)}
    OUT.mkdir(exist_ok=True)
    (OUT / "profile.json").write_text(
        json.dumps(report, sort_keys=True, indent=2))
    print(f"orders {len(orders)} rows, penguins {len(penguins)} rows")


if __name__ == "__main__":
    main()