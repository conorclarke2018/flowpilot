import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


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
