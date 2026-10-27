import { z } from "zod";

import { NODE_TYPES } from "./workflow";

// Runtime validation for a pasted/imported workflow definition — mirrors the
// backend's app/schemas/workflow_definition.py shape, with the same lenient
// defaults (source_handle/target_handle default to "output"/"input").
export const workflowNodeSchema = z.object({
  id: z.string().min(1),
  type: z.enum(NODE_TYPES),
  position: z.object({ x: z.number(), y: z.number() }),
  config: z.record(z.string(), z.unknown()).default({}),
});

export const workflowEdgeSchema = z.object({
  id: z.string().min(1),
  source: z.string().min(1),
  source_handle: z.string().default("output"),
  target: z.string().min(1),
  target_handle: z.string().default("input"),
});

export const workflowDefinitionSchema = z.object({
  schema_version: z.string().default("1.0"),
  name: z.string().min(1),
  nodes: z.array(workflowNodeSchema).default([]),
  edges: z.array(workflowEdgeSchema).default([]),
});

export type ImportedWorkflowDefinition = z.infer<typeof workflowDefinitionSchema>;
