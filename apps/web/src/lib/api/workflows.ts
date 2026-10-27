import { apiClient } from "./client";
import type {
  Approval,
  NodeRun,
  ValidationResponse,
  Workflow,
  WorkflowDefinition,
  WorkflowRun,
  WorkflowVersion,
  Workspace,
} from "../../types/workflow";

export function createWorkspace(name: string) {
  return apiClient.post<Workspace>("/workspaces", { name });
}

export function getWorkspace(workspaceId: string) {
  return apiClient.get<Workspace>(`/workspaces/${workspaceId}`);
}

export function listWorkflows(workspaceId: string) {
  return apiClient.get<Workflow[]>("/workflows", { workspace_id: workspaceId });
}

export function createWorkflow(
  workspaceId: string,
  name: string,
  definition: WorkflowDefinition,
) {
  return apiClient.post<Workflow>("/workflows", {
    workspace_id: workspaceId,
    name,
    definition,
  });
}

export function getWorkflow(workspaceId: string, workflowId: string) {
  return apiClient.get<Workflow>(`/workflows/${workflowId}`, { workspace_id: workspaceId });
}

export function updateWorkflowDraft(
  workspaceId: string,
  workflowId: string,
  definition: WorkflowDefinition,
) {
  return apiClient.put<Workflow>(
    `/workflows/${workflowId}`,
    { definition },
    { workspace_id: workspaceId },
  );
}

export function validateWorkflow(workspaceId: string, workflowId: string) {
  return apiClient.post<ValidationResponse>(
    `/workflows/${workflowId}/validate`,
    undefined,
    { workspace_id: workspaceId },
  );
}

export function publishWorkflow(workspaceId: string, workflowId: string) {
  return apiClient.post<WorkflowVersion>(
    `/workflows/${workflowId}/publish`,
    undefined,
    { workspace_id: workspaceId },
  );
}

export function createRun(
  workspaceId: string,
  workflowId: string,
  input: Record<string, unknown>,
) {
  return apiClient.post<WorkflowRun>(
    `/workflows/${workflowId}/runs`,
    { input },
    { workspace_id: workspaceId },
  );
}

export function getRun(workspaceId: string, runId: string) {
  return apiClient.get<WorkflowRun>(`/runs/${runId}`, { workspace_id: workspaceId });
}

export function getRunNodes(workspaceId: string, runId: string) {
  return apiClient.get<NodeRun[]>(`/runs/${runId}/nodes`, { workspace_id: workspaceId });
}

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
