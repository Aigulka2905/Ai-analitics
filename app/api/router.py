from fastapi import APIRouter

from app.api.routes import pro

api_router = APIRouter(prefix="/api")
api_router.include_router(pro.router)
