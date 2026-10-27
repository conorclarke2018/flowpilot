import { Button, Stack, Text } from "@mantine/core";

import { NODE_TYPES, type NodeType } from "../../types/workflow";

interface NodePaletteProps {
  onAdd: (nodeType: NodeType) => void;
}

export function NodePalette({ onAdd }: NodePaletteProps) {
  return (
    <Stack gap="xs" p="sm" w={220}>
      <Text fw={600} size="sm">
        Add node
      </Text>
      {NODE_TYPES.map((nodeType) => (
        <Button key={nodeType} variant="light" size="xs" onClick={() => onAdd(nodeType)}>
          {nodeType}
        </Button>
      ))}
    </Stack>
  );
}
