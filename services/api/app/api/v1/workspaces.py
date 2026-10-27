from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workspace import Workspace
from app.schemas.api import WorkspaceCreateRequest, WorkspaceResponse

router = APIRouter()


@router.post("/workspaces", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    payload: WorkspaceCreateRequest, db: Session = Depends(get_db)
) -> Workspace:
    workspace = Workspace(name=payload.name)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace
