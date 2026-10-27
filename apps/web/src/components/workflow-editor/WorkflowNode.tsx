import { Handle, type NodeProps, Position } from "@xyflow/react";

import type { NodeType } from "../../types/workflow";
import { styleForNodeType } from "./nodeStyles";

export interface WorkflowNodeData {
  nodeType: NodeType;
  config: Record<string, unknown>;
  [key: string]: unknown;
}

export function WorkflowNode({ data, selected, id }: NodeProps) {
  const nodeData = data as WorkflowNodeData;
  const style = styleForNodeType(nodeData.nodeType);

  return (
    <div
      role="group"
      aria-label={`${nodeData.nodeType} node ${id}`}
      style={{
        minWidth: 180,
        borderRadius: 8,
        border: `1.5px solid ${style.border}`,
        background: "var(--mantine-color-dark-6)",
        boxShadow: selected
          ? `0 0 0 2px ${style.color}, 0 4px 12px rgba(0,0,0,0.35)`
          : "0 2px 6px rgba(0,0,0,0.3)",
        overflow: "hidden",
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: style.color, width: 10, height: 10, border: "none" }}
      />

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 12px",
          background: style.background,
          borderBottom: `1px solid ${style.border}`,
        }}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke={style.color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d={style.icon} />
        </svg>
        <span style={{ fontSize: 12, fontWeight: 600, color: style.color }}>
          {nodeData.nodeType}
        </span>
      </div>

      <div style={{ padding: "6px 12px 10px" }}>
        <span style={{ fontSize: 11, color: "var(--mantine-color-dimmed)" }}>{id}</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: style.color, width: 10, height: 10, border: "none" }}
      />
    </div>
  );
}
