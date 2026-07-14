"""
backend/routers/transactions.py

GET    /api/transactions        -> list/search transaction history
DELETE /api/transactions/{id}   -> remove a transaction record
GET    /api/transactions/export -> download history as CSV
"""

import io
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
from backend.database import get_connection
from backend.schemas import TransactionRecord
from backend.logger import get_logger

router = APIRouter(prefix="/api", tags=["Transactions"])
logger = get_logger(__name__)


@router.get("/transactions", response_model=List[TransactionRecord])
def list_transactions(
    user: Optional[str] = Query(None, description="Filter by sender or receiver name"),
    date: Optional[str] = Query(None, description="Filter by date, format YYYY-MM-DD"),
    min_amount: Optional[float] = Query(None),
    risk_level: Optional[str] = Query(None),
    limit: int = Query(200, le=1000),
):
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    if user:
        query += " AND (sender_name LIKE ? OR receiver_name LIKE ?)"
        params.extend([f"%{user}%", f"%{user}%"])
    if date:
        query += " AND created_at LIKE ?"
        params.append(f"{date}%")
    if min_amount is not None:
        query += " AND amount >= ?"
        params.append(min_amount)
    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        {**dict(r), "previous_fraud_history": bool(r["previous_fraud_history"])}
        for r in rows
    ]


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
    logger.info("Deleted transaction id=%s", transaction_id)
    return {"message": f"Transaction {transaction_id} deleted"}


@router.get("/transactions/export")
def export_csv():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY created_at DESC", conn)

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finguard_transactions.csv"}
    )
