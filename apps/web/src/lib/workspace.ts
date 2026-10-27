import { useEffect, useState } from "react";

import { createWorkspace } from "./api/workflows";

const STORAGE_KEY = "flowpilot.workspace_id";

export function useWorkspaceId(): string | null {
  const [workspaceId, setWorkspaceId] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY),
  );

  useEffect(() => {
    if (workspaceId) return;

    createWorkspace("My Workspace").then((workspace) => {
      localStorage.setItem(STORAGE_KEY, workspace.id);
      setWorkspaceId(workspace.id);
    });
  }, [workspaceId]);

  return workspaceId;
}
