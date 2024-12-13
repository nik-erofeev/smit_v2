"""Корневой роутер приложения"""

from fastapi import APIRouter

from app.api.auth.router import router as auth_router
from app.api.blog.router import router as blog_router
from app.api.default.router import router as default_router
from app.api.tariff.router import router as tariff_router

router = APIRouter()


routers = (default_router, auth_router, blog_router, tariff_router)

for resource_router in routers:
    router.include_router(resource_router)
