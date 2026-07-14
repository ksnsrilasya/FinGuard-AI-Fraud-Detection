"""
backend/main.py

FastAPI application factory. Wires together config, logging, database,
and modular routers. Keeping this file thin (no business logic) is
what makes the architecture "clean" — main.py only assembles things.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db
from backend.logger import get_logger
from backend.routers import predict, transactions, dashboard, feedback

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Financial Fraud Detection Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("%s started in %s mode", settings.app_name, settings.app_env)


app.include_router(predict.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(feedback.router)


@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": settings.app_name}
