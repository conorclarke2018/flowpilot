import { apiClient } from "./client";
import type { Workspace } from "../../types/workspace";

export function createWorkspace(name: string) {
  return apiClient.post<Workspace>("/workspaces", { name });
}

export function getWorkspace(workspaceId: string) {
  return apiClient.get<Workspace>(`/workspaces/${workspaceId}`);
}
