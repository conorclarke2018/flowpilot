import { Badge, Button, Group, Loader, Stack, Text, Textarea, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { decideApproval, listPendingApprovals } from "../../lib/api/workflows";
import { useWorkspaceId } from "../../lib/workspace";
import type { Approval } from "../../types/workflow";

function ApprovalCard({ approval, workspaceId }: { approval: Approval; workspaceId: string }) {
  const queryClient = useQueryClient();
  const [text, setText] = useState(() => JSON.stringify(approval.proposed_payload, null, 2));
  const [error, setError] = useState<string | null>(null);

  const decide = useMutation({
    mutationFn: (decision: "approved" | "rejected") => {
      if (decision === "rejected") {
        return decideApproval(workspaceId, approval.id, "rejected");
      }
      let payload: Record<string, unknown>;
      try {
        payload = JSON.parse(text);
        setError(null);
      } catch {
        setError("Payload must be valid JSON");
        throw new Error("invalid json");
      }
      return decideApproval(workspaceId, approval.id, "approved", payload);
    },
    onSuccess: (_, decision) => {
      queryClient.invalidateQueries({ queryKey: ["approvals", workspaceId] });
      notifications.show({
        message: decision === "approved" ? "Approved — run resumed" : "Rejected — run cancelled",
        color: decision === "approved" ? "green" : "red",
      });
    },
  });

  return (
    <Stack gap="xs" p="md" style={{ border: "1px solid var(--mantine-color-dark-4)", borderRadius: 8 }}>
      <Group justify="space-between">
        <Text fw={600} size="sm">
          {approval.node_id}
        </Text>
        <Badge size="xs">run {approval.workflow_run_id.slice(0, 8)}</Badge>
      </Group>
      <Textarea
        autosize
        minRows={4}
        value={text}
        onChange={(event) => setText(event.currentTarget.value)}
        error={error}
      />
      <Group gap="xs">
        <Button
          size="xs"
          loading={decide.isPending && decide.variables === "approved"}
          onClick={() => decide.mutate("approved")}
        >
          Approve
        </Button>
        <Button
          size="xs"
          color="red"
          variant="light"
          loading={decide.isPending && decide.variables === "rejected"}
          onClick={() => decide.mutate("rejected")}
        >
          Reject
        </Button>
      </Group>
    </Stack>
  );
}

export function ApprovalsPage() {
  const workspaceId = useWorkspaceId();

  const approvalsQuery = useQuery({
    queryKey: ["approvals", workspaceId],
    queryFn: () => listPendingApprovals(workspaceId as string),
    enabled: Boolean(workspaceId),
    refetchInterval: 5000,
  });

  if (!workspaceId || approvalsQuery.isLoading) {
    return <Loader />;
  }

  const approvals = approvalsQuery.data ?? [];

  return (
    <Stack>
      <Title order={2}>Approval inbox</Title>
      {approvals.length === 0 && <Text c="dimmed">No pending approvals.</Text>}
      {approvals.map((approval) => (
        <ApprovalCard key={approval.id} approval={approval} workspaceId={workspaceId} />
      ))}
    </Stack>
  );
}
