# scripts/train.py

import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import joblib

# This script trains a simple logistic regression model on the clinvar features
# and saves the trained model to a file.
# It is a very simple example of a training script, and it could be improved
# in many ways. For example, you could:
#
# - Use a more sophisticated model, such as a gradient boosting model
# - Tune the hyperparameters of the model
# - Use a more sophisticated cross-validation strategy
# - Use a more sophisticated evaluation metric
# - Add logging and monitoring
# - Add a command-line interface to the script
#
# However, this script is a good starting point for a more complex training
# pipeline.

# Set up the logger
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


# Load the data
# Note: we are using a simplified dataset for this example
# In a real-world scenario, you would have a more complex data loading and preprocessing pipeline
# For example, you might have a separate script to generate the features
# and then load them here
logging.info("Loading data...")
df = pd.read_parquet("data/clinvar_features.parquet")
X = df.drop("is_pathogenic", axis=1)
y = df["is_pathogenic"]  # <-- FIX IS HERE

# Create a simple logistic regression model
clf = LogisticRegression(random_state=42)

# Create a cross-validation strategy
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Evaluate the model using cross-validation
# We are using roc_auc as the evaluation metric
logging.info("Starting cross-validation...")
auc = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc", n_jobs=-1).mean()
logging.info(f"Cross-validation ROC AUC: {auc:.4f}")

# Train the model on the full dataset
logging.info("Training model on full dataset...")
clf.fit(X, y)

# Save the trained model to a file
logging.info("Saving model to models/model.joblib...")
joblib.dump(clf, "models/model.joblib")

logging.info("Done.")