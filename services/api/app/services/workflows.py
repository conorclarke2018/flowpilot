import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine.validation import WorkflowValidationResult, validate_workflow
from app.models.workflow import Workflow, WorkflowVersion
from app.schemas.workflow import WorkflowDefinition


class WorkflowNotFoundError(Exception):
    pass


class PublishValidationError(Exception):
    def __init__(self, result: WorkflowValidationResult) -> None:
        self.result = result
        super().__init__("Workflow definition failed validation")


def create_workflow(
    db: Session,
    *,
    workspace_id: uuid.UUID,
    name: str,
    description: str | None,
    definition: WorkflowDefinition,
) -> Workflow:
    workflow = Workflow(
        workspace_id=workspace_id,
        name=name,
        description=description,
        draft_definition=definition.model_dump(mode="json"),
        draft_revision=1,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def list_workflows(db: Session, *, workspace_id: uuid.UUID) -> list[Workflow]:
    stmt = select(Workflow).where(Workflow.workspace_id == workspace_id)
    return list(db.scalars(stmt))


def get_workflow(db: Session, *, workspace_id: uuid.UUID, workflow_id: uuid.UUID) -> Workflow:
    stmt = select(Workflow).where(
        Workflow.id == workflow_id, Workflow.workspace_id == workspace_id
    )
    workflow = db.scalars(stmt).first()
    if workflow is None:
        raise WorkflowNotFoundError(str(workflow_id))
    return workflow


def update_draft(
    db: Session,
    *,
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    definition: WorkflowDefinition,
) -> Workflow:
    workflow = get_workflow(db, workspace_id=workspace_id, workflow_id=workflow_id)
    workflow.draft_definition = definition.model_dump(mode="json")
    workflow.draft_revision += 1
    db.commit()
    db.refresh(workflow)
    return workflow


def validate_draft(
    db: Session, *, workspace_id: uuid.UUID, workflow_id: uuid.UUID
) -> WorkflowValidationResult:
    workflow = get_workflow(db, workspace_id=workspace_id, workflow_id=workflow_id)
    definition = WorkflowDefinition.model_validate(workflow.draft_definition)
    return validate_workflow(definition)


def publish_workflow(
    db: Session, *, workspace_id: uuid.UUID, workflow_id: uuid.UUID
) -> WorkflowVersion:
    workflow = get_workflow(db, workspace_id=workspace_id, workflow_id=workflow_id)
    definition = WorkflowDefinition.model_validate(workflow.draft_definition)

    result = validate_workflow(definition)
    if not result.is_valid:
        raise PublishValidationError(result)

    next_version = (workflow.published_version or 0) + 1
    version = WorkflowVersion(
        workflow_id=workflow.id,
        version=next_version,
        definition=definition.model_dump(mode="json"),
    )
    workflow.published_version = next_version
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
