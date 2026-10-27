import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    node_id: str
    status: str
    proposed_payload: dict[str, Any]
    decided_payload: dict[str, Any] | None
    created_at: datetime
    decided_at: datetime | None


class ApprovalDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    payload: dict[str, Any] | None = None
