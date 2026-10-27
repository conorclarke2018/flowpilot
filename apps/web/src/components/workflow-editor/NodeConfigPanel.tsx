import { Button, Stack, Text, Textarea } from "@mantine/core";
import { useState } from "react";

interface NodeConfigPanelProps {
  nodeId: string;
  nodeType: string;
  config: Record<string, unknown>;
  onApply: (nodeId: string, config: Record<string, unknown>) => void;
  onDelete: (nodeId: string) => void;
}

// Keyed by nodeId from the parent, so switching the selected node remounts
// this component instead of needing an effect to resync local text state.
export function NodeConfigPanel({
  nodeId,
  nodeType,
  config,
  onApply,
  onDelete,
}: NodeConfigPanelProps) {
  const [text, setText] = useState(() => JSON.stringify(config, null, 2));
  const [error, setError] = useState<string | null>(null);

  const apply = () => {
    try {
      const parsed = JSON.parse(text);
      setError(null);
      onApply(nodeId, parsed);
    } catch {
      setError("Config must be valid JSON");
    }
  };

  return (
    <Stack gap="xs" p="sm" w={320}>
      <Text fw={600} size="sm">
        {nodeType}
      </Text>
      <Text size="xs" c="dimmed">
        {nodeId}
      </Text>
      <Textarea
        label="Node configuration (JSON)"
        autosize
        minRows={8}
        value={text}
        onChange={(event) => setText(event.currentTarget.value)}
        error={error}
      />
      <Button size="xs" onClick={apply}>
        Apply config
      </Button>
      <Button size="xs" color="red" variant="light" onClick={() => onDelete(nodeId)}>
        Delete node
      </Button>
    </Stack>
  );
}
