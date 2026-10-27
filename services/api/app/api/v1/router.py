from fastapi import APIRouter

from app.api.v1.approvals import router as approvals_router
from app.api.v1.health import router as health_router
from app.api.v1.runs import router as runs_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(workspaces_router)
api_router.include_router(workflows_router)
api_router.include_router(runs_router)
api_router.include_router(approvals_router)
