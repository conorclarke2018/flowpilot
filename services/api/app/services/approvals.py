import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.run import WorkflowRun
from app.models.workflow import Workflow


class ApprovalNotFoundError(Exception):
    pass


class ApprovalAlreadyDecidedError(Exception):
    pass


def get_approval(db: Session, *, workspace_id: uuid.UUID, approval_id: uuid.UUID) -> Approval:
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise ApprovalNotFoundError(str(approval_id))

    owned = db.scalars(
        select(Approval)
        .join(WorkflowRun, Approval.workflow_run_id == WorkflowRun.id)
        .join(Workflow, WorkflowRun.workflow_id == Workflow.id)
        .where(Approval.id == approval_id, Workflow.workspace_id == workspace_id)
    ).first()
    if owned is None:
        raise ApprovalNotFoundError(str(approval_id))
    return approval


def list_pending_approvals(db: Session, *, workspace_id: uuid.UUID) -> list[Approval]:
    stmt = (
        select(Approval)
        .join(WorkflowRun, Approval.workflow_run_id == WorkflowRun.id)
        .join(Workflow, WorkflowRun.workflow_id == Workflow.id)
        .where(Workflow.workspace_id == workspace_id, Approval.status == "pending")
        .order_by(Approval.created_at)
    )
    return list(db.scalars(stmt))


def decide_approval(
    db: Session,
    *,
    workspace_id: uuid.UUID,
    approval_id: uuid.UUID,
    decision: Literal["approved", "rejected"],
    payload: dict[str, Any] | None = None,
) -> Approval:
    approval = get_approval(db, workspace_id=workspace_id, approval_id=approval_id)
    if approval.status != "pending":
        raise ApprovalAlreadyDecidedError(str(approval_id))

    approval.status = decision
    approval.decided_at = datetime.now(UTC)

    run = db.get(WorkflowRun, approval.workflow_run_id)

    if decision == "approved":
        approval.decided_payload = payload if payload is not None else approval.proposed_payload
        run.status = "queued"
    else:
        approval.decided_payload = None
        run.status = "cancelled"
        run.finished_at = datetime.now(UTC)

    db.commit()
    db.refresh(approval)
    return approval
