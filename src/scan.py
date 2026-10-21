from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1] # the repo, from the file
DATA = ROOT / "data" / "retail_orders_week1.csv"

def scan(df):
    y = df['returned']
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    results = []
    for col in df.columns:
        if col in ['order_id', 'order_date', 'customer_id', 'returned']:
            continue
        # fit on that column alone, 5-fold, score roc_auc
        if pd.api.types.is_numeric_dtype(df[col]):
            transform = make_pipeline(SimpleImputer(strategy='median'), StandardScaler())
        else:
            transform = OneHotEncoder(handle_unknown='ignore')
        pre = ColumnTransformer([('col', transform, [col])])
        model = make_pipeline(pre, LogisticRegression(max_iter=2000))
        score = cross_val_score(model, df[[col]], y, cv=cv, scoring='roc_auc').mean()
        results.append((col, round(float(score), 4)))
    return (pd.DataFrame(results, columns=['column', 'roc_auc_cv'])
            .sort_values('roc_auc_cv', ascending=False)
            .reset_index(drop=True))

def main():
    df = pd.read_csv(DATA)
    print(scan(df).to_string(index=False))

if __name__ == "__main__":
    main()