export const NODE_TYPES = [
  "trigger.manual",
  "trigger.webhook",
  "data.transform",
  "ai.classify",
  "logic.condition",
  "human.approval",
  "action.mock_email",
  "action.webhook",
] as const;

export type NodeType = (typeof NODE_TYPES)[number];

export interface NodePosition {
  x: number;
  y: number;
}

export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: NodePosition;
  config: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  source_handle: string;
  target: string;
  target_handle: string;
}

export interface WorkflowDefinition {
  schema_version: string;
  name: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface Workflow {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  draft_definition: WorkflowDefinition;
  draft_revision: number;
  published_version: number | null;
  created_at: string;
  updated_at: string;
}

export interface ValidationError {
  code: string;
  message: string;
}

export interface ValidationResponse {
  is_valid: boolean;
  errors: ValidationError[];
}

export interface WorkflowVersion {
  id: string;
  workflow_id: string;
  version: number;
  definition: WorkflowDefinition;
  created_at: string;
}

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

export interface Workspace {
  id: string;
  name: string;
  created_at: string;
}

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
