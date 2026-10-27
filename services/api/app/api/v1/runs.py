import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import NodeRunResponse, RunCreateRequest, RunResponse
from app.services import runs as run_service
from app.services.runs import RunNotFoundError, WorkflowNotPublishedError
from app.services.workflows import WorkflowNotFoundError
from app.workers.tasks import execute_run_task

router = APIRouter()


@router.post("/workflows/{workflow_id}/runs", response_model=RunResponse, status_code=202)
async def create_run(
    workflow_id: uuid.UUID,
    payload: RunCreateRequest,
    workspace_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
) -> RunResponse:
    try:
        run = run_service.create_run(
            db,
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            input_data=payload.input,
            idempotency_key=payload.idempotency_key,
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    except WorkflowNotPublishedError:
        raise HTTPException(
            status_code=422, detail="Workflow must be published before it can run"
        ) from None

    if run.status == "queued":
        execute_run_task.delay(str(run.id))
        db.refresh(run)

    return RunResponse.model_validate(run, from_attributes=True)


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: uuid.UUID, workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> RunResponse:
    try:
        run = run_service.get_run(db, workspace_id=workspace_id, run_id=run_id)
    except RunNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found") from None
    return RunResponse.model_validate(run, from_attributes=True)


@router.get("/runs/{run_id}/nodes", response_model=list[NodeRunResponse])
async def get_run_nodes(
    run_id: uuid.UUID, workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> list[NodeRunResponse]:
    try:
        node_runs = run_service.list_node_runs(db, workspace_id=workspace_id, run_id=run_id)
    except RunNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found") from None
    return [NodeRunResponse.model_validate(nr, from_attributes=True) for nr in node_runs]
