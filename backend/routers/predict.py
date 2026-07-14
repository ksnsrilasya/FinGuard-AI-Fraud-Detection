"""
backend/routers/predict.py

POST /api/predict
Validates a transaction, runs it through the ML service, persists the
result, and returns a structured prediction response.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.schemas import TransactionInput, PredictionResponse
from backend.database import get_connection
from backend.ml_service import predict_transaction
from backend.logger import get_logger

router = APIRouter(prefix="/api", tags=["Prediction"])
logger = get_logger(__name__)


@router.post("/predict", response_model=PredictionResponse)
def predict(txn: TransactionInput):
    try:
        result = predict_transaction(txn)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO transactions
                   (sender_name, receiver_name, amount, merchant_category,
                    transaction_type, device_type, location, transaction_hour,
                    previous_fraud_history, customer_age, payment_method,
                    fraud_probability, confidence_score, risk_level, reasons, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    txn.sender_name, txn.receiver_name, txn.amount, txn.merchant_category,
                    txn.transaction_type, txn.device_type, txn.location, txn.transaction_hour,
                    int(txn.previous_fraud_history), txn.customer_age, txn.payment_method,
                    result["fraud_probability"], result["confidence_score"],
                    result["risk_level"], ", ".join(result["reasons"]),
                    datetime.utcnow().isoformat()
                )
            )
            transaction_id = cursor.lastrowid
    except Exception as e:
        logger.exception("Failed to persist transaction")
        raise HTTPException(status_code=500, detail=f"Failed to save transaction: {e}")

    return PredictionResponse(**result, transaction_id=transaction_id)
