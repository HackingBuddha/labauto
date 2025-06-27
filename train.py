#!/usr/bin/env python
"""Train logistic‑regression pathogenicity model."""

import argparse
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data/clinvar_features.parquet")
ap.add_argument("--model", default="data/variant_lr.pkl")
args = ap.parse_args()

df = pd.read_parquet(args.data)
X = df[["DP", "AF", "CADD"]].fillna(0)
y = (df["QUAL"] == ".").astype(int)  # toy label, swap for real CLNSIG

clf = LogisticRegression(max_iter=500, class_weight="balanced").fit(X, y)
print("AUC", roc_auc_score(y, clf.predict_proba(X)[:, 1]))

joblib.dump(clf, args.model)
print("✅ saved", args.model)
