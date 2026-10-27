import { Badge, Group, Loader, Paper, SimpleGrid, Stack, Table, Text, Title } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { listPendingApprovals } from "../../lib/api/approvals";
import { listWorkflows } from "../../lib/api/workflows";
import { useWorkspaceId } from "../../lib/workspace";

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent: string;
}) {
  return (
    <Paper
      p="md"
      withBorder
      style={{ borderLeft: `3px solid ${accent}` }}
      role="group"
      aria-label={`${label}: ${value}`}
    >
      <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
        {label}
      </Text>
      <Text size="xl" fw={700}>
        {value}
      </Text>
    </Paper>
  );
}

export function DashboardPage() {
  const workspaceId = useWorkspaceId();

  const workflowsQuery = useQuery({
    queryKey: ["workflows", workspaceId],
    queryFn: () => listWorkflows(workspaceId as string),
    enabled: Boolean(workspaceId),
  });

  const approvalsQuery = useQuery({
    queryKey: ["approvals", workspaceId],
    queryFn: () => listPendingApprovals(workspaceId as string),
    enabled: Boolean(workspaceId),
    refetchInterval: 5000,
  });

  if (!workspaceId || workflowsQuery.isLoading) {
    return <Loader />;
  }

  const workflows = workflowsQuery.data ?? [];
  const published = workflows.filter((w) => w.published_version !== null);
  const drafts = workflows.filter((w) => w.published_version === null);
  const pendingApprovals = approvalsQuery.data ?? [];

  return (
    <Stack>
      <Title order={2}>Dashboard</Title>

      <SimpleGrid cols={{ base: 1, sm: 3 }}>
        <StatCard label="Workflows" value={workflows.length} accent="#4dabf7" />
        <StatCard label="Published" value={published.length} accent="#51cf66" />
        <StatCard label="Pending approvals" value={pendingApprovals.length} accent="#ff922b" />
      </SimpleGrid>

      <Stack gap="xs">
        <Title order={4}>Recent workflows</Title>
        {workflows.length === 0 ? (
          <Text c="dimmed" size="sm">
            No workflows yet —{" "}
            <Text component={Link} to="/workflows" c="blue" span>
              create one
            </Text>
            .
          </Text>
        ) : (
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
                {workflows.slice(0, 5).map((workflow) => (
                  <Table.Tr key={workflow.id}>
                    <Table.Td>
                      <Text component={Link} to={`/workflows/${workflow.id}`} c="blue">
                        {workflow.name}
                      </Text>
                    </Table.Td>
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
        )}
      </Stack>

      {pendingApprovals.length > 0 && (
        <Stack gap="xs">
          <Group gap="xs">
            <Title order={4}>Needs your attention</Title>
            <Badge color="orange">{pendingApprovals.length} pending</Badge>
          </Group>
          <Text size="sm">
            <Text component={Link} to="/approvals" c="blue" span>
              Go to the approval inbox
            </Text>{" "}
            to review and resume paused runs.
          </Text>
        </Stack>
      )}

      {drafts.length > 0 && (
        <Text size="xs" c="dimmed">
          {drafts.length} workflow{drafts.length === 1 ? "" : "s"} still in draft and not yet
          published.
        </Text>
      )}
    </Stack>
  );
}
