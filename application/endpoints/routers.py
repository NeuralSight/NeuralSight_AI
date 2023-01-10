from fastapi import APIRouter
from endpoints import login, users, report
api_router = APIRouter()
api_router.include_router(login.router, tags=["Users"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(report.router, prefix="/patient", tags=["Reports"])
