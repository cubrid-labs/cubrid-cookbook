from __future__ import annotations

from fastapi import APIRouter

from .tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(tasks_router, tags=["tasks"])
