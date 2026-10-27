from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.providers.base import ModelProvider
from app.providers.factory import get_provider

SessionDep = Annotated[Session, Depends(get_db)]
ProviderDep = Annotated[ModelProvider, Depends(get_provider)]
