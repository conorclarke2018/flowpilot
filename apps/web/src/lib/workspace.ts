import { useEffect, useRef, useState } from "react";

import { ApiError } from "./api/client";
import { createWorkspace, getWorkspace } from "./api/workspaces";

const STORAGE_KEY = "flowpilot.workspace_id";

async function resolveWorkspaceId(): Promise<string> {
  const cached = localStorage.getItem(STORAGE_KEY);

  if (cached) {
    try {
      await getWorkspace(cached);
      return cached;
    } catch (error) {
      // Stale id (e.g. pointing at a workspace from a reset database) —
      // fall through and mint a fresh one rather than getting stuck forever.
      if (!(error instanceof ApiError) || error.status !== 404) {
        throw error;
      }
    }
  }

  const workspace = await createWorkspace("My Workspace");
  localStorage.setItem(STORAGE_KEY, workspace.id);
  return workspace.id;
}

export function useWorkspaceId(): string | null {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const resolving = useRef(false);

  useEffect(() => {
    if (workspaceId || resolving.current) return;
    resolving.current = true;

    resolveWorkspaceId()
      .then(setWorkspaceId)
      .finally(() => {
        resolving.current = false;
      });
  }, [workspaceId]);

  return workspaceId;
}
