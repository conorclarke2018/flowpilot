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

export interface GenerateWorkflowResponse {
  definition: WorkflowDefinition;
  is_valid: boolean;
  errors: ValidationError[];
  attempts: number;
}
