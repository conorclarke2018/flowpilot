import { apiClient } from "./client";
import type {
  GenerateWorkflowResponse,
  ValidationResponse,
  Workflow,
  WorkflowDefinition,
  WorkflowVersion,
} from "../../types/workflow";

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
  name?: string,
) {
  return apiClient.put<Workflow>(
    `/workflows/${workflowId}`,
    { definition, name },
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

export function generateWorkflow(workspaceId: string, workflowId: string, prompt: string) {
  return apiClient.post<GenerateWorkflowResponse>(
    `/workflows/${workflowId}/generate`,
    { prompt },
    { workspace_id: workspaceId },
  );
}

export function deleteWorkflow(workspaceId: string, workflowId: string) {
  return apiClient.delete<void>(`/workflows/${workflowId}`, { workspace_id: workspaceId });
}
