import { Alert, Badge, Button, Group, Stack, Table, Text, Textarea } from "@mantine/core";
import { useState } from "react";

import { createRun, getRun, getRunNodes } from "../../lib/api/runs";
import type { NodeRun, WorkflowRun } from "../../types/run";

const TERMINAL_STATUSES = new Set(["succeeded", "failed", "cancelled"]);

interface TestRunPanelProps {
  workspaceId: string;
  workflowId: string;
  isPublished: boolean;
}

async function waitForCompletion(workspaceId: string, runId: string): Promise<WorkflowRun> {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    const run = await getRun(workspaceId, runId);
    if (TERMINAL_STATUSES.has(run.status)) {
      return run;
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  return getRun(workspaceId, runId);
}

export function TestRunPanel({ workspaceId, workflowId, isPublished }: TestRunPanelProps) {
  const [inputText, setInputText] = useState("{}");
  const [inputError, setInputError] = useState<string | null>(null);
  const [run, setRun] = useState<WorkflowRun | null>(null);
  const [nodeRuns, setNodeRuns] = useState<NodeRun[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const handleRun = async () => {
    let parsedInput: Record<string, unknown>;
    try {
      parsedInput = JSON.parse(inputText);
      setInputError(null);
    } catch {
      setInputError("Input must be valid JSON");
      return;
    }

    setIsRunning(true);
    setRun(null);
    setNodeRuns([]);
    try {
      const created = await createRun(workspaceId, workflowId, parsedInput);
      const finished = await waitForCompletion(workspaceId, created.id);
      setRun(finished);
      setNodeRuns(await getRunNodes(workspaceId, finished.id));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Stack gap="xs" p="sm" w={360}>
      <Text fw={600} size="sm">
        Test run
      </Text>
      {!isPublished && (
        <Alert color="yellow" title="Not published">
          Publish the workflow before running it.
        </Alert>
      )}
      <Textarea
        label="Sample input (JSON)"
        autosize
        minRows={4}
        value={inputText}
        onChange={(event) => setInputText(event.currentTarget.value)}
        error={inputError}
      />
      <Button loading={isRunning} disabled={!isPublished} onClick={handleRun}>
        Run
      </Button>

      {run && (
        <Stack gap={4}>
          <Group gap="xs">
            <Text size="sm">Status:</Text>
            <Badge color={run.status === "succeeded" ? "green" : "red"}>{run.status}</Badge>
          </Group>
          {run.error && (
            <Text size="xs" c="red">
              {run.error}
            </Text>
          )}
        </Stack>
      )}

      {nodeRuns.length > 0 && (
        <Table fz="xs">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Node</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Output / error</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {nodeRuns.map((nodeRun) => (
              <Table.Tr key={nodeRun.id}>
                <Table.Td>{nodeRun.node_id}</Table.Td>
                <Table.Td>
                  <Badge size="xs" color={nodeRun.status === "succeeded" ? "green" : "red"}>
                    {nodeRun.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" c={nodeRun.error ? "red" : undefined} style={{ wordBreak: "break-all" }}>
                    {nodeRun.error ?? JSON.stringify(nodeRun.output)}
                  </Text>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Stack>
  );
}
