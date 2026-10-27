import { ActionIcon, Badge, Button, Group, Loader, Modal, Stack, Table, Text, TextInput, Title, Tooltip } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createWorkflow, deleteWorkflow, listWorkflows, updateWorkflowDraft } from "../../lib/api/workflows";
import { useWorkspaceId } from "../../lib/workspace";
import type { Workflow, WorkflowDefinition } from "../../types/workflow";

const BLANK_DEFINITION: WorkflowDefinition = {
  schema_version: "1.0",
  name: "Untitled workflow",
  nodes: [],
  edges: [],
};

function RenameIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
      <path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z" />
    </svg>
  );
}

export function WorkflowsPage() {
  const workspaceId = useWorkspaceId();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [renameTarget, setRenameTarget] = useState<Workflow | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<Workflow | null>(null);

  const workflowsQuery = useQuery({
    queryKey: ["workflows", workspaceId],
    queryFn: () => listWorkflows(workspaceId as string),
    enabled: Boolean(workspaceId),
  });

  const createMutation = useMutation({
    mutationFn: () => createWorkflow(workspaceId as string, "Untitled workflow", BLANK_DEFINITION),
    onSuccess: (workflow) => {
      queryClient.invalidateQueries({ queryKey: ["workflows", workspaceId] });
      navigate(`/workflows/${workflow.id}`);
    },
    onError: () => {
      notifications.show({ message: "Could not create workflow", color: "red" });
    },
  });

  const renameMutation = useMutation({
    mutationFn: () => {
      if (!renameTarget) throw new Error("no rename target");
      const trimmed = renameValue.trim();
      if (!trimmed) throw new Error("empty name");
      return updateWorkflowDraft(
        workspaceId as string,
        renameTarget.id,
        renameTarget.draft_definition,
        trimmed,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows", workspaceId] });
      notifications.show({ message: "Workflow renamed", color: "green" });
      setRenameTarget(null);
    },
    onError: (err) => {
      if (err instanceof Error && (err.message === "empty name" || err.message === "no rename target")) return;
      notifications.show({ message: "Could not rename workflow", color: "red" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      if (!deleteTarget) throw new Error("no delete target");
      return deleteWorkflow(workspaceId as string, deleteTarget.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows", workspaceId] });
      notifications.show({ message: "Workflow deleted", color: "green" });
      setDeleteTarget(null);
    },
    onError: () => {
      notifications.show({ message: "Could not delete workflow", color: "red" });
    },
  });

  if (!workspaceId || workflowsQuery.isLoading) {
    return <Loader />;
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Workflows</Title>
        <Button loading={createMutation.isPending} onClick={() => createMutation.mutate()}>
          New workflow
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={560}>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Draft revision</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {workflowsQuery.data?.map((workflow) => (
              <Table.Tr
                key={workflow.id}
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/workflows/${workflow.id}`)}
              >
                <Table.Td>{workflow.name}</Table.Td>
                <Table.Td>
                  {workflow.published_version ? (
                    <Badge color="green">Published v{workflow.published_version}</Badge>
                  ) : (
                    <Badge color="gray">Draft</Badge>
                  )}
                </Table.Td>
                <Table.Td>{workflow.draft_revision}</Table.Td>
                <Table.Td>
                  <Group gap={4} justify="flex-end" wrap="nowrap">
                    <Tooltip label="Rename">
                      <ActionIcon
                        variant="subtle"
                        aria-label={`Rename ${workflow.name}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          setRenameTarget(workflow);
                          setRenameValue(workflow.name);
                        }}
                      >
                        <RenameIcon />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Delete">
                      <ActionIcon
                        variant="subtle"
                        color="red"
                        aria-label={`Delete ${workflow.name}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          setDeleteTarget(workflow);
                        }}
                      >
                        <DeleteIcon />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal opened={renameTarget !== null} onClose={() => setRenameTarget(null)} title="Rename workflow">
        <Stack gap="sm">
          <TextInput
            label="Name"
            value={renameValue}
            onChange={(event) => setRenameValue(event.currentTarget.value)}
            data-autofocus
          />
          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setRenameTarget(null)}>
              Cancel
            </Button>
            <Button loading={renameMutation.isPending} onClick={() => renameMutation.mutate()}>
              Save
            </Button>
          </Group>
        </Stack>
      </Modal>

      <Modal opened={deleteTarget !== null} onClose={() => setDeleteTarget(null)} title="Delete workflow">
        <Stack gap="sm">
          <Text size="sm">
            Delete <strong>{deleteTarget?.name}</strong>? This permanently removes its draft,
            published versions, and run history. This cannot be undone.
          </Text>
          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button color="red" loading={deleteMutation.isPending} onClick={() => deleteMutation.mutate()}>
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
