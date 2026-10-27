from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.runs import router as runs_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.workspaces import router as workspaces_router
from app.core.config import settings

app = FastAPI(title="FlowPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(workspaces_router, prefix="/api/v1")
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
