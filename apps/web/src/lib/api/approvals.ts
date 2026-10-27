import { apiClient } from "./client";
import type { Approval } from "../../types/approval";

export function listPendingApprovals(workspaceId: string) {
  return apiClient.get<Approval[]>("/approvals", { workspace_id: workspaceId });
}

export function decideApproval(
  workspaceId: string,
  approvalId: string,
  decision: "approved" | "rejected",
  payload?: Record<string, unknown>,
) {
  return apiClient.post<Approval>(
    `/approvals/${approvalId}/decision`,
    { decision, payload },
    { workspace_id: workspaceId },
  );
}
