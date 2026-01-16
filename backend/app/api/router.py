from fastapi import APIRouter

from app.api.routes import auth, imports, orders, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(orders.router)
api_router.include_router(imports.router)
api_router.include_router(users.router)
