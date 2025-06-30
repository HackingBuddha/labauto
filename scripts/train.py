#!/usr/bin/env python
"""
Train a logistic‑regression variant‑pathogenicity classifier.

* Expects a Parquet produced by **feature_engineering.py** that contains a
  `CLNSIG` column with ClinVar clinical significance labels (e.g. Pathogenic,
  Benign). If the column is missing, it falls back to QUAL‑based dummy labels
  but will **exit** if that yields only one class—avoids the ValueError you
  hit.
"""

import argparse
import joblib
import sys
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, StratifiedKFold

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data/clinvar_features.parquet")
ap.add_argument("--model", default="data/variant_lr.pkl")
args = ap.parse_args()

df = pd.read_parquet(args.data)

# Prefer real ClinVar labels if present
if "CLNSIG" in df.columns:
    y = df["CLNSIG"].isin(["Pathogenic", "Likely_pathogenic"]).astype(int)
else:
    print("⚠️  CLNSIG column not found; falling back to QUAL dummy labels")
    y = (df["QUAL"] == ".").astype(int)

if y.nunique() < 2:
    sys.exit("❌  Need at least two classes for training; check your labels.")

X = df[[c for c in ["DP", "AF", "CADD"] if c in df.columns]].fillna(0)

X = df[["DP", "AF", "CADD", "SpliceAI_DS", "gnomAD_AF"]].fillna(0)
y = ...

clf = LogisticRegression(max_iter=1000, class_weight="balanced")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
auc = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc", n_jobs=-1).mean()
print(f"CV AUROC = {auc:.3f}")

clf.fit(X, y)

y_prob = clf.predict_proba(X)[:, 1]
auc = roc_auc_score(y, y_prob)
print(f"AUC  {auc:.3f}")

joblib.dump(clf, args.model)
print("✅ saved", args.model)
