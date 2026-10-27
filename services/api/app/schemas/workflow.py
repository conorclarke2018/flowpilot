import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.workflow_definition import WorkflowDefinition


class WorkflowCreateRequest(BaseModel):
    workspace_id: uuid.UUID
    name: str
    description: str | None = None
    definition: WorkflowDefinition


class WorkflowUpdateRequest(BaseModel):
    definition: WorkflowDefinition


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    draft_definition: WorkflowDefinition
    draft_revision: int
    published_version: int | None
    created_at: datetime
    updated_at: datetime


class ValidationErrorResponse(BaseModel):
    code: str
    message: str


class ValidationResponse(BaseModel):
    is_valid: bool
    errors: list[ValidationErrorResponse]


class WorkflowVersionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version: int
    definition: WorkflowDefinition
    created_at: datetime


class GenerateWorkflowRequest(BaseModel):
    prompt: str


class GenerateWorkflowResponse(BaseModel):
    definition: WorkflowDefinition
    is_valid: bool
    errors: list[ValidationErrorResponse]
    attempts: int
