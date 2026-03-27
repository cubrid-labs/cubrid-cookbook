from __future__ import annotations

from fastapi import APIRouter

from app.routes.health import router as health_router
from app.routes.items import router as items_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(items_router)
