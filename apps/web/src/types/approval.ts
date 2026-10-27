export type ApprovalStatus = "pending" | "approved" | "rejected";

export interface Approval {
  id: string;
  workflow_run_id: string;
  node_id: string;
  status: ApprovalStatus;
  proposed_payload: Record<string, unknown>;
  decided_payload: Record<string, unknown> | null;
  created_at: string;
  decided_at: string | null;
}
