import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.workflow import WorkflowDefinition


class WorkspaceCreateRequest(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime


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


class RunCreateRequest(BaseModel):
    input: dict[str, Any]
    idempotency_key: str | None = None


class RunResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    workflow_version: int
    status: str
    input: dict[str, Any]
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class NodeRunResponse(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    node_id: str
    status: str
    output: dict[str, Any] | None
    error: str | None
    started_at: datetime
    finished_at: datetime


class GenerateWorkflowRequest(BaseModel):
    prompt: str


class GenerateWorkflowResponse(BaseModel):
    definition: WorkflowDefinition
    is_valid: bool
    errors: list[ValidationErrorResponse]
    attempts: int
