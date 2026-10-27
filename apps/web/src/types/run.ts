export type RunStatus =
  | "queued"
  | "running"
  | "waiting_for_approval"
  | "succeeded"
  | "failed"
  | "cancelled";

export interface WorkflowRun {
  id: string;
  workflow_id: string;
  workflow_version: number;
  status: RunStatus;
  input: Record<string, unknown>;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface NodeRun {
  id: string;
  workflow_run_id: string;
  node_id: string;
  status: "succeeded" | "failed";
  output: Record<string, unknown> | null;
  error: string | null;
  started_at: string;
  finished_at: string;
}
