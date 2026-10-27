import type { NodeType } from "../../types/workflow";

export interface NodeCategoryStyle {
  color: string;
  background: string;
  border: string;
  icon: string; // inline SVG path data, 24x24 viewBox, stroke-based
}

// Color-coded by role so a workflow's shape is readable at a glance:
// entry points, data/AI processing, branching, human-in-the-loop, and
// side-effecting actions each get a distinct, dark-mode-safe accent.
const CATEGORY_STYLES: Record<string, NodeCategoryStyle> = {
  trigger: {
    color: "#4dabf7",
    background: "rgba(77, 171, 247, 0.12)",
    border: "#4dabf7",
    icon: "M13 3L4 14h6l-1 7 9-11h-6l1-7z",
  },
  data: {
    color: "#da77f2",
    background: "rgba(218, 119, 242, 0.12)",
    border: "#da77f2",
    icon: "M4 7h16M4 7l4-4M4 7l4 4M20 17H4M20 17l-4-4M20 17l-4 4",
  },
  ai: {
    color: "#9775fa",
    background: "rgba(151, 117, 250, 0.12)",
    border: "#9775fa",
    icon: "M12 3l1.8 4.6L18 9.5l-4.2 1.9L12 16l-1.8-4.6L6 9.5l4.2-1.9L12 3zM19 14l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z",
  },
  logic: {
    color: "#ffd43b",
    background: "rgba(255, 212, 59, 0.12)",
    border: "#ffd43b",
    icon: "M6 3v6a3 3 0 003 3h6a3 3 0 003-3V3M6 15v6M18 15v6M6 9h12",
  },
  approval: {
    color: "#ff922b",
    background: "rgba(255, 146, 43, 0.12)",
    border: "#ff922b",
    icon: "M9 12l2 2 4-4M12 3a9 9 0 100 18 9 9 0 000-18z",
  },
  action: {
    color: "#51cf66",
    background: "rgba(81, 207, 102, 0.12)",
    border: "#51cf66",
    icon: "M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z",
  },
};

const FALLBACK_STYLE: NodeCategoryStyle = {
  color: "#adb5bd",
  background: "rgba(173, 181, 189, 0.12)",
  border: "#adb5bd",
  icon: "M12 2a10 10 0 100 20 10 10 0 000-20z",
};

export function categoryForNodeType(nodeType: NodeType): string {
  return nodeType.split(".")[0] === "human" ? "approval" : nodeType.split(".")[0];
}

export function styleForNodeType(nodeType: NodeType): NodeCategoryStyle {
  return CATEGORY_STYLES[categoryForNodeType(nodeType)] ?? FALLBACK_STYLE;
}
