import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

ROOT = Path.cwd() if (Path.cwd() / "src").exists() else Path.cwd().parent
sys.path.insert(0, str(ROOT / "src"))
from features import TARGET, build_pipeline, cv_auc, feature_frame

orders = pd.read_csv(ROOT / "data" / "orders_clean.csv")
X, y = feature_frame(orders), orders[TARGET]

models = {
    "logistic regression": LogisticRegression(max_iter=2000),
    "decision tree, depth 4": DecisionTreeClassifier(max_depth=4, random_state=0),
    "gradient boosting": GradientBoostingClassifier(random_state=0),
    "random forest": RandomForestClassifier(random_state=0),
}

def parameters(est):
    """Weights for a linear model, tree nodes for anything built from trees."""
    if hasattr(est, "coef_"):
        return f"{est.coef_.size} weights"
    trees = [est] if hasattr(est, "tree_") else list(np.ravel(est.estimators_))
    return f"{sum(t.tree_.node_count for t in trees):,} tree nodes"

for name, m in models.items():
    pipe = build_pipeline().set_params(model=m)
    auc = cv_auc(pipe, X, y)
    fitted = pipe.fit(X, y)
    size_kb = round(len(pickle.dumps(fitted)) / 1024, 1)
    print(f"{name:24s} ROC-AUC {auc['mean']:.4f} sd {auc['sd']:.4f}   "
          f"{size_kb:>9,.1f} KB   {parameters(fitted.named_steps['model'])}")