"""
backend/routers/feedback.py

POST /api/feedback -> analyst marks a prediction as correct/incorrect.
This is the hook that would feed a future retraining pipeline
(labelled feedback -> periodic model refresh).
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.schemas import FeedbackInput
from backend.database import get_connection

router = APIRouter(prefix="/api", tags=["Feedback"])


@router.post("/feedback")
def submit_feedback(feedback: FeedbackInput):
    with get_connection() as conn:
        txn = conn.execute(
            "SELECT id FROM transactions WHERE id = ?", (feedback.transaction_id,)
        ).fetchone()
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")

        conn.execute(
            """INSERT INTO feedback (transaction_id, is_correct, notes, created_at)
               VALUES (?, ?, ?, ?)""",
            (feedback.transaction_id, int(feedback.is_correct), feedback.notes,
             datetime.utcnow().isoformat())
        )
    return {"message": "Feedback recorded", "transaction_id": feedback.transaction_id}
