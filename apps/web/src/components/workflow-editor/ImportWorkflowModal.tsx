import { Button, List, Modal, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";

import { workflowDefinitionSchema } from "../../types/workflow.schema";
import type { WorkflowDefinition } from "../../types/workflow";

interface ImportWorkflowModalProps {
  opened: boolean;
  onClose: () => void;
  onImport: (definition: WorkflowDefinition) => void;
}

const PLACEHOLDER = `{
  "schema_version": "1.0",
  "name": "My workflow",
  "nodes": [
    { "id": "trigger_1", "type": "trigger.manual", "position": { "x": 0, "y": 0 }, "config": {} }
  ],
  "edges": []
}`;

export function ImportWorkflowModal({ opened, onClose, onImport }: ImportWorkflowModalProps) {
  const [text, setText] = useState("");
  const [errors, setErrors] = useState<string[]>([]);

  const handleImport = () => {
    let raw: unknown;
    try {
      raw = JSON.parse(text);
    } catch {
      setErrors(["Not valid JSON — check for a missing comma or bracket."]);
      return;
    }

    const result = workflowDefinitionSchema.safeParse(raw);
    if (!result.success) {
      setErrors(
        result.error.issues.map((issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`),
      );
      return;
    }

    setErrors([]);
    onImport(result.data as WorkflowDefinition);
    setText("");
    onClose();
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Import workflow JSON" size="lg">
      <Stack gap="sm">
        <Text size="sm" c="dimmed">
          Paste a full workflow definition (name, nodes, edges). This replaces everything
          currently on the canvas — save or publish first if you want to keep it.
        </Text>
        <Textarea
          label="Workflow definition (JSON)"
          placeholder={PLACEHOLDER}
          autosize
          minRows={12}
          maxRows={24}
          value={text}
          onChange={(event) => setText(event.currentTarget.value)}
          styles={{ input: { fontFamily: "monospace" } }}
        />
        {errors.length > 0 && (
          <List size="sm" c="red" spacing={2}>
            {errors.map((error, index) => (
              <List.Item key={index}>{error}</List.Item>
            ))}
          </List>
        )}
        <Button onClick={handleImport} disabled={!text.trim()}>
          Import
        </Button>
      </Stack>
    </Modal>
  );
}
