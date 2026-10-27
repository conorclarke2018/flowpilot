import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine.executor import execute_workflow
from app.models.approval import Approval
from app.models.run import NodeRun, WorkflowRun
from app.models.workflow import WorkflowVersion
from app.schemas.workflow_definition import WorkflowDefinition
from app.services.workflows import WorkflowNotFoundError, get_workflow


class WorkflowNotPublishedError(Exception):
    pass


class RunNotFoundError(Exception):
    pass


def create_run(
    db: Session,
    *,
    workspace_id: uuid.UUID,
    workflow_id: uuid.UUID,
    input_data: dict[str, Any],
    idempotency_key: str | None = None,
) -> WorkflowRun:
    workflow = get_workflow(db, workspace_id=workspace_id, workflow_id=workflow_id)
    if workflow.published_version is None:
        raise WorkflowNotPublishedError(str(workflow_id))

    if idempotency_key is not None:
        existing = db.scalars(
            select(WorkflowRun).where(
                WorkflowRun.workflow_id == workflow_id,
                WorkflowRun.idempotency_key == idempotency_key,
            )
        ).first()
        if existing is not None:
            return existing

    run = WorkflowRun(
        workflow_id=workflow_id,
        workflow_version=workflow.published_version,
        status="queued",
        input=input_data,
        idempotency_key=idempotency_key,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _known_node_outputs(db: Session, *, run_id: uuid.UUID) -> dict[str, dict[str, Any]]:
    outputs: dict[str, dict[str, Any]] = {}

    node_runs = db.scalars(
        select(NodeRun).where(NodeRun.workflow_run_id == run_id, NodeRun.status == "succeeded")
    )
    for node_run in node_runs:
        outputs[node_run.node_id] = node_run.output or {}

    approved = db.scalars(
        select(Approval).where(
            Approval.workflow_run_id == run_id, Approval.status == "approved"
        )
    )
    for approval in approved:
        outputs[approval.node_id] = approval.decided_payload or {}

    return outputs


def execute_run(db: Session, *, run_id: uuid.UUID) -> WorkflowRun:
    run = db.get(WorkflowRun, run_id)
    if run is None:
        raise RunNotFoundError(str(run_id))

    if run.status != "queued":
        return run

    run.status = "running"
    if run.started_at is None:
        run.started_at = datetime.now(UTC)
    db.commit()

    version = db.scalars(
        select(WorkflowVersion).where(
            WorkflowVersion.workflow_id == run.workflow_id,
            WorkflowVersion.version == run.workflow_version,
        )
    ).first()
    definition = WorkflowDefinition.model_validate(version.definition)
    known_outputs = _known_node_outputs(db, run_id=run.id)

    result = execute_workflow(definition, run.input, known_node_outputs=known_outputs)

    for node_result in result.node_results:
        db.add(
            NodeRun(
                workflow_run_id=run.id,
                node_id=node_result.node_id,
                status=node_result.status,
                output=node_result.output,
                error=node_result.error,
                started_at=node_result.started_at,
                finished_at=node_result.finished_at,
            )
        )

    if result.status == "waiting_for_approval":
        existing_pending = db.scalars(
            select(Approval).where(
                Approval.workflow_run_id == run.id,
                Approval.node_id == result.pending_approval_node_id,
                Approval.status == "pending",
            )
        ).first()
        if existing_pending is None:
            db.add(
                Approval(
                    workflow_run_id=run.id,
                    node_id=result.pending_approval_node_id,
                    proposed_payload=result.pending_approval_payload or {},
                    status="pending",
                )
            )
        run.status = "waiting_for_approval"
    else:
        run.status = result.status
        run.finished_at = datetime.now(UTC)
        if result.status == "failed":
            failed_node = next(r for r in result.node_results if r.status == "failed")
            run.error = failed_node.error

    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, *, workspace_id: uuid.UUID, run_id: uuid.UUID) -> WorkflowRun:
    run = db.get(WorkflowRun, run_id)
    if run is None:
        raise RunNotFoundError(str(run_id))
    try:
        get_workflow(db, workspace_id=workspace_id, workflow_id=run.workflow_id)
    except WorkflowNotFoundError:
        raise RunNotFoundError(str(run_id)) from None
    return run


def list_node_runs(
    db: Session, *, workspace_id: uuid.UUID, run_id: uuid.UUID
) -> list[NodeRun]:
    run = get_run(db, workspace_id=workspace_id, run_id=run_id)
    stmt = select(NodeRun).where(NodeRun.workflow_run_id == run.id).order_by(NodeRun.started_at)
    return list(db.scalars(stmt))
