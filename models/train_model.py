"""
models/train_model.py

Trains and evaluates the FinGuard fraud detection model.

Pipeline:
1. Load data
2. Encode categorical features
3. Train/test split (stratified, since fraud is rare)
4. Train Random Forest (class_weight="balanced")
5. Evaluate: classification report, confusion matrix, ROC-AUC/ROC curve
6. Save model + encoders + feature order + evaluation plots
"""

import os
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")  # headless rendering, no display needed
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    confusion_matrix, ConfusionMatrixDisplay
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "models", "data", "transactions.csv")
ARTIFACT_DIR = os.path.join(BASE_DIR, "models", "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# ---------- 1. Load ----------
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} rows from {DATA_PATH}")

# ---------- 2. Feature engineering ----------
categorical_cols = ["merchant_category", "transaction_type", "device_type",
                     "location", "payment_method"]
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col])
    encoders[col] = le

feature_cols = [
    "amount", "transaction_hour", "customer_age", "previous_fraud_history",
    "merchant_category_enc", "transaction_type_enc", "device_type_enc",
    "location_enc", "payment_method_enc",
]
X = df[feature_cols]
y = df["is_fraud"]

# ---------- 3. Train/test split ----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------- 4. Train ----------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train, y_train)

# ---------- 5. Evaluate ----------
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

report = classification_report(y_test, y_pred, target_names=["Legit", "Fraud"])
auc = roc_auc_score(y_test, y_proba)
print("Classification Report:\n", report)
print(f"ROC-AUC: {auc:.4f}")

# Confusion matrix plot
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(5, 4))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Legit", "Fraud"])
disp.plot(ax=ax, cmap="Blues", colorbar=False)
plt.title("FinGuard — Confusion Matrix")
plt.tight_layout()
plt.savefig(os.path.join(ARTIFACT_DIR, "confusion_matrix.png"), dpi=150)
plt.close()

# ROC curve plot
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(5, 4))
plt.plot(fpr, tpr, label=f"ROC curve (AUC = {auc:.3f})", color="#38bdf8")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("FinGuard — ROC Curve")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(ARTIFACT_DIR, "roc_curve.png"), dpi=150)
plt.close()

# Feature importance plot
importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values()
plt.figure(figsize=(6, 4))
importances.plot(kind="barh", color="#38bdf8")
plt.title("FinGuard — Feature Importance")
plt.tight_layout()
plt.savefig(os.path.join(ARTIFACT_DIR, "feature_importance.png"), dpi=150)
plt.close()

print("\nFeature Importances:")
for col, imp in importances.sort_values(ascending=False).items():
    print(f"  {col}: {imp:.4f}")

# ---------- 6. Save artifacts ----------
joblib.dump(model, os.path.join(ARTIFACT_DIR, "fraud_model.pkl"))
joblib.dump(encoders, os.path.join(ARTIFACT_DIR, "encoders.pkl"))
joblib.dump(feature_cols, os.path.join(ARTIFACT_DIR, "feature_cols.pkl"))

with open(os.path.join(ARTIFACT_DIR, "evaluation_report.txt"), "w") as f:
    f.write(f"FinGuard Model Evaluation\n{'='*40}\n\n")
    f.write(report)
    f.write(f"\nROC-AUC: {auc:.4f}\n")

print(f"\nSaved model artifacts + evaluation plots to {ARTIFACT_DIR}")
