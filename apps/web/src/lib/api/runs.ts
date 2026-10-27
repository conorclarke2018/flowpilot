import { apiClient } from "./client";
import type { NodeRun, WorkflowRun } from "../../types/run";

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
