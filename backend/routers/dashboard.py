"""
backend/routers/dashboard.py

GET /api/dashboard -> summary stats + risk distribution for the dashboard UI
"""

from fastapi import APIRouter
from backend.database import get_connection
from backend.schemas import DashboardStats

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        fraud = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE risk_level = 'High Risk'"
        ).fetchone()[0]
        low = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE risk_level = 'Low Risk'"
        ).fetchone()[0]
        medium = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE risk_level = 'Medium Risk'"
        ).fetchone()[0]
        high = fraud

    safe = total - fraud
    fraud_pct = round((fraud / total) * 100, 2) if total else 0.0

    return DashboardStats(
        total_transactions=total,
        fraud_transactions=fraud,
        safe_transactions=safe,
        fraud_percentage=fraud_pct,
        risk_distribution={"Low Risk": low, "Medium Risk": medium, "High Risk": high},
    )
