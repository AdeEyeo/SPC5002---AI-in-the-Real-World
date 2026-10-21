from pathlib import Path
import json, hashlib, platform
import pandas as pd, sklearn
ROOT = Path(__file__).resolve().parents[1] # the repo, from the file
DATA = ROOT / "data" / "retail_orders_week1.csv"
OUT = ROOT / "outputs"
def evaluate(df):
    ... # <-- your notebook logic
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score
    from sklearn.preprocessing import StandardScaler

    # record the raw dataset before any filtering (slide 15 expects 2,030 rows)
    n_rows = len(df)
    n_columns = df.shape[1]
    n_returns = df['returned'].sum()
    base_rate = df['returned'].mean()

    # drop the rows that look wrong, and put VAT on the order value
    df = df[df['quantity'] > 0]
    df = df[df['delivery_days'] > 0]
    df = df.assign(order_value_incl_vat=df['order_value'] * 1.2)
    len(df)

    sample = df.sample(1200, random_state=7)
    sample['returned'].mean()

    features = ['item_price', 'discount_pct', 'quantity',
                'delivery_days', 'customer_prior_orders']

    X = df[features]
    y = df['returned']

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=7, stratify=y)

    model = LogisticRegression(max_iter=2000)
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print('ROC-AUC', round(auc, 3))

    coefs = pd.Series(model.coef_[0], index=features).sort_values()

    summary = (df.groupby('category')['returned']
    .mean()
    .sort_values(ascending=False)
    .rename('return_rate')
    .reset_index())

    return {
        "n_rows": int(n_rows),
        "n_columns": int(n_columns),
        "n_returns": int(n_returns),
        "base_rate": round(float(base_rate), 4),
        "seed": 7,
        "features": features,
        "n_rows_after_filter": int(len(df)),
        "sample_return_rate": round(float(sample['returned'].mean()), 4),
        "roc_auc": round(float(auc), 4),
        "coefficients": {k: round(float(v), 4) for k, v in coefs.items()},
        "return_rate_by_category": {
            cat: round(float(rate), 4)
            for cat, rate in zip(summary['category'], summary['return_rate'])
            },
        "provenance": {
            "data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest()[:16],
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            },
        }

def main():
    df = pd.read_csv(DATA)
    OUT.mkdir(exist_ok=True)
    (OUT / "metrics.json").write_text(
        json.dumps(evaluate(df), sort_keys=True, indent=2))
if __name__ == "__main__":
    main()