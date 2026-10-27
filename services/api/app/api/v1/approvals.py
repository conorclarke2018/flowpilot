import uuid

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import SessionDep
from app.schemas.api import ApprovalDecisionRequest, ApprovalResponse
from app.services import approvals as approval_service
from app.services.approvals import ApprovalAlreadyDecidedError, ApprovalNotFoundError
from app.workers.tasks import execute_run_task

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse])
async def list_pending_approvals(
    db: SessionDep, workspace_id: uuid.UUID = Query(...)
) -> list[ApprovalResponse]:
    approvals = approval_service.list_pending_approvals(db, workspace_id=workspace_id)
    return [ApprovalResponse.model_validate(a, from_attributes=True) for a in approvals]


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
async def decide_approval(
    approval_id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    db: SessionDep,
    workspace_id: uuid.UUID = Query(...),
) -> ApprovalResponse:
    try:
        approval = approval_service.decide_approval(
            db,
            workspace_id=workspace_id,
            approval_id=approval_id,
            decision=payload.decision,
            payload=payload.payload,
        )
    except ApprovalNotFoundError:
        raise HTTPException(status_code=404, detail="Approval not found") from None
    except ApprovalAlreadyDecidedError:
        raise HTTPException(status_code=409, detail="Approval already decided") from None

    if payload.decision == "approved":
        execute_run_task.delay(str(approval.workflow_run_id))

    return ApprovalResponse.model_validate(approval, from_attributes=True)
