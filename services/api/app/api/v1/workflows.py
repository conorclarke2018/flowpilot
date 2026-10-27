import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.providers.base import ModelProvider
from app.providers.factory import get_provider
from app.schemas.api import (
    GenerateWorkflowRequest,
    GenerateWorkflowResponse,
    ValidationErrorResponse,
    ValidationResponse,
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowUpdateRequest,
    WorkflowVersionResponse,
)
from app.services import workflows as workflow_service
from app.services.generation import generate_workflow_proposal
from app.services.workflows import PublishValidationError, WorkflowNotFoundError

router = APIRouter()


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    payload: WorkflowCreateRequest, db: Session = Depends(get_db)
) -> WorkflowResponse:
    workflow = workflow_service.create_workflow(
        db,
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        definition=payload.definition,
    )
    return WorkflowResponse.model_validate(workflow, from_attributes=True)


@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows(
    workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> list[WorkflowResponse]:
    workflows = workflow_service.list_workflows(db, workspace_id=workspace_id)
    return [WorkflowResponse.model_validate(w, from_attributes=True) for w in workflows]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID, workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> WorkflowResponse:
    try:
        workflow = workflow_service.get_workflow(
            db, workspace_id=workspace_id, workflow_id=workflow_id
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    return WorkflowResponse.model_validate(workflow, from_attributes=True)


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_draft(
    workflow_id: uuid.UUID,
    payload: WorkflowUpdateRequest,
    workspace_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
) -> WorkflowResponse:
    try:
        workflow = workflow_service.update_draft(
            db,
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            definition=payload.definition,
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    return WorkflowResponse.model_validate(workflow, from_attributes=True)


@router.post("/workflows/{workflow_id}/validate", response_model=ValidationResponse)
async def validate_workflow_draft(
    workflow_id: uuid.UUID, workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> ValidationResponse:
    try:
        result = workflow_service.validate_draft(
            db, workspace_id=workspace_id, workflow_id=workflow_id
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    return ValidationResponse(
        is_valid=result.is_valid,
        errors=[ValidationErrorResponse(code=e.code, message=e.message) for e in result.errors],
    )


@router.post("/workflows/{workflow_id}/publish", response_model=WorkflowVersionResponse)
async def publish_workflow(
    workflow_id: uuid.UUID, workspace_id: uuid.UUID = Query(...), db: Session = Depends(get_db)
) -> WorkflowVersionResponse:
    try:
        version = workflow_service.publish_workflow(
            db, workspace_id=workspace_id, workflow_id=workflow_id
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    except PublishValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {"code": e.code, "message": e.message} for e in exc.result.errors
            ],
        ) from None
    return WorkflowVersionResponse.model_validate(version, from_attributes=True)


@router.post("/workflows/{workflow_id}/generate", response_model=GenerateWorkflowResponse)
async def generate_workflow(
    workflow_id: uuid.UUID,
    payload: GenerateWorkflowRequest,
    workspace_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    provider: ModelProvider = Depends(get_provider),
) -> GenerateWorkflowResponse:
    try:
        workflow_service.get_workflow(db, workspace_id=workspace_id, workflow_id=workflow_id)
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None

    definition, result, attempts = await generate_workflow_proposal(provider, payload.prompt)

    return GenerateWorkflowResponse(
        definition=definition,
        is_valid=result.is_valid,
        errors=[ValidationErrorResponse(code=e.code, message=e.message) for e in result.errors],
        attempts=attempts,
    )
