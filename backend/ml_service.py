"""
backend/ml_service.py

Encapsulates all ML concerns: loading the trained model/encoders and
turning a validated TransactionInput into a fraud prediction + a
plain-language explanation. Keeping this separate from the API routes
means the model can be swapped/retrained without touching route code.
"""

import os
import numpy as np
import pandas as pd
import joblib
from backend.config import settings
from backend.schemas import TransactionInput
from backend.logger import get_logger

logger = get_logger(__name__)

_model = None
_encoders = None
_feature_cols = None


def load_artifacts():
    global _model, _encoders, _feature_cols

    if _model is None:
        model_path = os.path.join(settings.model_dir, "fraud_model.pkl")
        encoders_path = os.path.join(settings.model_dir, "encoders.pkl")
        features_path = os.path.join(settings.model_dir, "feature_cols.pkl")

        logger.debug("Model dir: %s", settings.model_dir)
        logger.debug("Model path: %s", model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Run `python models/train_model.py` first to train and save the model artifacts."
            )

        _model = joblib.load(model_path)
        _encoders = joblib.load(encoders_path)
        _feature_cols = joblib.load(features_path)

        logger.info("ML model artifacts loaded from %s", settings.model_dir)

    return _model, _encoders, _feature_cols


def _safe_encode(encoder, value: str) -> int:
    """Encode a category; unseen categories fall back to an 'unknown' bucket
    instead of crashing the API."""
    if value in encoder.classes_:
        return int(encoder.transform([value])[0])
    return len(encoder.classes_)


def _risk_level(prob: float) -> str:
    if prob < 0.3:
        return "Low Risk"
    elif prob < 0.65:
        return "Medium Risk"
    return "High Risk"


def _explain(txn: TransactionInput) -> list:
    reasons = []
    if txn.amount > 1000:
        reasons.append("High transaction amount")
    if txn.transaction_hour in [0, 1, 2, 3, 4]:
        reasons.append("Unusual transaction time (late night)")
    if "New" in txn.device_type:
        reasons.append("Unrecognized/new device")
    if txn.location == "Unknown/Foreign":
        reasons.append("Unusual or foreign location")
    if txn.merchant_category in ["Crypto Exchange", "Jewelry"]:
        reasons.append("High-risk merchant category")
    if txn.previous_fraud_history:
        reasons.append("Customer has prior fraud history")
    if txn.payment_method in ["Wire Transfer", "Cryptocurrency"]:
        reasons.append("High-risk payment method")
    if txn.customer_age < 25 and txn.amount > 800:
        reasons.append("Large transaction relative to customer profile")
    if not reasons:
        reasons.append("No significant risk factors detected")
    return reasons


def predict_transaction(txn: TransactionInput) -> dict:
    model, encoders, feature_cols = load_artifacts()

    encoded = {
        "amount": txn.amount,
        "transaction_hour": txn.transaction_hour,
        "customer_age": txn.customer_age,
        "previous_fraud_history": int(txn.previous_fraud_history),
        "merchant_category_enc": _safe_encode(encoders["merchant_category"], txn.merchant_category),
        "transaction_type_enc": _safe_encode(encoders["transaction_type"], txn.transaction_type),
        "device_type_enc": _safe_encode(encoders["device_type"], txn.device_type),
        "location_enc": _safe_encode(encoders["location"], txn.location),
        "payment_method_enc": _safe_encode(encoders["payment_method"], txn.payment_method),
    }

    X = pd.DataFrame([[encoded[col] for col in feature_cols]], columns=feature_cols)
    proba = float(model.predict_proba(X)[0][1])

    # Confidence score: how far the model's probability is from the 0.5
    # decision boundary, scaled to 0-100. A prediction of 0.98 or 0.02 is
    # "confident"; 0.51 is not.
    confidence = round((abs(proba - 0.5) / 0.5) * 100, 2)

    result = {
        "fraud_probability": round(proba * 100, 2),
        "confidence_score": confidence,
        "risk_level": _risk_level(proba),
        "reasons": _explain(txn),
    }
    logger.info(
        "Prediction generated | risk=%s | probability=%.2f%%",
        result["risk_level"], result["fraud_probability"]
    )
    return result
