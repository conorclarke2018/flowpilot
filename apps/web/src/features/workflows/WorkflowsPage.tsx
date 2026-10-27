import { Badge, Button, Group, Loader, Stack, Table, Title } from "@mantine/core";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { createWorkflow, listWorkflows } from "../../lib/api/workflows";
import { useWorkspaceId } from "../../lib/workspace";
import type { WorkflowDefinition } from "../../types/workflow";

const BLANK_DEFINITION: WorkflowDefinition = {
  schema_version: "1.0",
  name: "Untitled workflow",
  nodes: [],
  edges: [],
};

export function WorkflowsPage() {
  const workspaceId = useWorkspaceId();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

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

      <Table.ScrollContainer minWidth={480}>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Draft revision</Table.Th>
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
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>
    </Stack>
  );
}
