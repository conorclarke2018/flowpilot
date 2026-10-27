import uuid

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import ProviderDep, SessionDep
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

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(payload: WorkflowCreateRequest, db: SessionDep) -> WorkflowResponse:
    workflow = workflow_service.create_workflow(
        db,
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        definition=payload.definition,
    )
    return WorkflowResponse.model_validate(workflow, from_attributes=True)


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    db: SessionDep, workspace_id: uuid.UUID = Query(...)
) -> list[WorkflowResponse]:
    workflows = workflow_service.list_workflows(db, workspace_id=workspace_id)
    return [WorkflowResponse.model_validate(w, from_attributes=True) for w in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID, db: SessionDep, workspace_id: uuid.UUID = Query(...)
) -> WorkflowResponse:
    try:
        workflow = workflow_service.get_workflow(
            db, workspace_id=workspace_id, workflow_id=workflow_id
        )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found") from None
    return WorkflowResponse.model_validate(workflow, from_attributes=True)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_draft(
    workflow_id: uuid.UUID,
    payload: WorkflowUpdateRequest,
    db: SessionDep,
    workspace_id: uuid.UUID = Query(...),
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


@router.post("/{workflow_id}/validate", response_model=ValidationResponse)
async def validate_workflow_draft(
    workflow_id: uuid.UUID, db: SessionDep, workspace_id: uuid.UUID = Query(...)
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


@router.post("/{workflow_id}/publish", response_model=WorkflowVersionResponse)
async def publish_workflow(
    workflow_id: uuid.UUID, db: SessionDep, workspace_id: uuid.UUID = Query(...)
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
            detail=[{"code": e.code, "message": e.message} for e in exc.result.errors],
        ) from None
    return WorkflowVersionResponse.model_validate(version, from_attributes=True)


@router.post("/{workflow_id}/generate", response_model=GenerateWorkflowResponse)
async def generate_workflow(
    workflow_id: uuid.UUID,
    payload: GenerateWorkflowRequest,
    db: SessionDep,
    provider: ProviderDep,
    workspace_id: uuid.UUID = Query(...),
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
