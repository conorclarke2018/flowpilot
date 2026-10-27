import uuid
from datetime import datetime

from pydantic import BaseModel


class WorkspaceCreateRequest(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
