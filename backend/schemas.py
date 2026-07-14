"""
backend/schemas.py

Pydantic models for request validation and response shaping.
Keeping these separate from DB logic follows clean architecture:
API contract is independent of storage details.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class TransactionInput(BaseModel):
    sender_name: str = Field(..., min_length=1, max_length=100)
    receiver_name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant_category: str
    transaction_type: str = Field(..., description="e.g. Transfer, Withdrawal, Purchase, Deposit")
    device_type: str
    location: str
    transaction_hour: int = Field(..., ge=0, le=23)
    previous_fraud_history: bool = False
    customer_age: int = Field(..., ge=18, le=100)
    payment_method: str


class PredictionResponse(BaseModel):
    fraud_probability: float
    confidence_score: float
    risk_level: str
    reasons: List[str]
    transaction_id: int


class TransactionRecord(TransactionInput):
    id: int
    fraud_probability: float
    confidence_score: float
    risk_level: str
    reasons: str
    created_at: str


class DashboardStats(BaseModel):
    total_transactions: int
    fraud_transactions: int
    safe_transactions: int
    fraud_percentage: float
    risk_distribution: dict


class FeedbackInput(BaseModel):
    transaction_id: int
    is_correct: bool
    notes: Optional[str] = None
