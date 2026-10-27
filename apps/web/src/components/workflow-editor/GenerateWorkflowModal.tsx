import { Alert, Badge, Button, Group, List, Modal, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";

import { generateWorkflow } from "../../lib/api/workflows";
import type { GenerateWorkflowResponse, WorkflowDefinition } from "../../types/workflow";

interface GenerateWorkflowModalProps {
  opened: boolean;
  onClose: () => void;
  workspaceId: string;
  workflowId: string;
  onGenerated: (definition: WorkflowDefinition) => void;
}

export function GenerateWorkflowModal({
  opened,
  onClose,
  workspaceId,
  workflowId,
  onGenerated,
}: GenerateWorkflowModalProps) {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateWorkflowResponse | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setResult(null);
    try {
      const response = await generateWorkflow(workspaceId, workflowId, prompt);
      setResult(response);
      onGenerated(response.definition);
    } catch {
      setError("Could not generate a workflow — try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    setPrompt("");
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <Modal opened={opened} onClose={handleClose} title="Generate workflow with AI" size="lg">
      <Stack gap="sm">
        <Text size="sm" c="dimmed">
          Describe the automation in plain language. The model proposes a graph using only
          supported node types — review and edit it on the canvas before publishing; nothing
          runs or saves automatically.
        </Text>
        <Textarea
          label="What should this workflow do?"
          placeholder="Classify incoming customer enquiries, flag urgent messages, and prepare a response for review."
          autosize
          minRows={3}
          maxRows={8}
          value={prompt}
          onChange={(event) => setPrompt(event.currentTarget.value)}
        />
        <Button onClick={handleGenerate} loading={isGenerating} disabled={!prompt.trim()}>
          Generate
        </Button>

        {error && (
          <Alert color="red" title="Generation failed">
            {error}
          </Alert>
        )}

        {result && (
          <Stack gap={4}>
            <Group gap="xs">
              <Text size="sm">Result:</Text>
              <Badge color={result.is_valid ? "green" : "yellow"}>
                {result.is_valid ? "Valid" : "Needs edits"}
              </Badge>
              <Text size="xs" c="dimmed">
                {result.attempts} attempt{result.attempts === 1 ? "" : "s"}
              </Text>
            </Group>
            <Text size="xs" c="dimmed">
              Loaded onto the canvas — close this dialog to review it.
            </Text>
            {!result.is_valid && result.errors.length > 0 && (
              <List size="xs" c="yellow">
                {result.errors.map((err, index) => (
                  <List.Item key={index}>
                    [{err.code}] {err.message}
                  </List.Item>
                ))}
              </List>
            )}
          </Stack>
        )}
      </Stack>
    </Modal>
  );
}
