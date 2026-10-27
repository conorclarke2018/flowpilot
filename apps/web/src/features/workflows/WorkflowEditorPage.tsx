import "@xyflow/react/dist/style.css";

import { Alert, Badge, Button, Group, Loader, Stack, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addEdge,
  Background,
  type Connection,
  Controls,
  type Edge,
  MarkerType,
  type Node,
  type OnConnect,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { NodeConfigPanel } from "../../components/workflow-editor/NodeConfigPanel";
import { NodePalette } from "../../components/workflow-editor/NodePalette";
import { nodeTypes, WORKFLOW_NODE_TYPE } from "../../components/workflow-editor/nodeTypes";
import type { WorkflowNodeData } from "../../components/workflow-editor/WorkflowNode";
import { TestRunPanel } from "../../components/execution-viewer/TestRunPanel";
import { ApiError } from "../../lib/api/client";
import {
  getWorkflow,
  publishWorkflow,
  updateWorkflowDraft,
  validateWorkflow,
} from "../../lib/api/workflows";
import { useWorkspaceId } from "../../lib/workspace";
import type { NodeType, ValidationError, WorkflowDefinition } from "../../types/workflow";

type FlowNodeData = WorkflowNodeData;

function definitionToFlow(definition: WorkflowDefinition): {
  nodes: Node<FlowNodeData>[];
  edges: Edge[];
} {
  return {
    nodes: definition.nodes.map((node) => ({
      id: node.id,
      type: WORKFLOW_NODE_TYPE,
      position: node.position,
      data: { nodeType: node.type, config: node.config },
    })),
    edges: definition.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
    })),
  };
}

function flowToDefinition(
  name: string,
  nodes: Node<FlowNodeData>[],
  edges: Edge[],
): WorkflowDefinition {
  return {
    schema_version: "1.0",
    name,
    nodes: nodes.map((node) => ({
      id: node.id,
      type: node.data.nodeType,
      position: { x: node.position.x, y: node.position.y },
      config: node.data.config,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      source_handle: "output",
      target: edge.target,
      target_handle: "input",
    })),
  };
}

let nodeCounter = 0;

export function WorkflowEditorPage() {
  const { workflowId } = useParams<{ workflowId: string }>();
  const workspaceId = useWorkspaceId();
  const queryClient = useQueryClient();

  const workflowQuery = useQuery({
    queryKey: ["workflow", workspaceId, workflowId],
    queryFn: () => getWorkflow(workspaceId as string, workflowId as string),
    enabled: Boolean(workspaceId && workflowId),
  });

  const [nodes, setNodes, onNodesChange] = useNodesState<Node<FlowNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationError[] | null>(null);

  useEffect(() => {
    if (!workflowQuery.data) return;
    const { nodes: initialNodes, edges: initialEdges } = definitionToFlow(
      workflowQuery.data.draft_definition,
    );
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [workflowQuery.data, setNodes, setEdges]);

  const onConnect: OnConnect = useCallback(
    (connection: Connection) =>
      setEdges((eds) => addEdge({ ...connection, id: `edge_${Date.now()}` }, eds)),
    [setEdges],
  );

  const addNode = useCallback(
    (nodeType: NodeType) => {
      nodeCounter += 1;
      const id = `${nodeType.replace(".", "_")}_${nodeCounter}`;
      setNodes((current) => [
        ...current,
        {
          id,
          type: WORKFLOW_NODE_TYPE,
          position: { x: 80 + current.length * 40, y: 80 + current.length * 60 },
          data: { nodeType, config: {} },
        },
      ]);
    },
    [setNodes],
  );

  const applyNodeConfig = useCallback(
    (nodeId: string, config: Record<string, unknown>) => {
      setNodes((current) =>
        current.map((node) =>
          node.id === nodeId ? { ...node, data: { ...node.data, config } } : node,
        ),
      );
    },
    [setNodes],
  );

  const deleteNode = useCallback(
    (nodeId: string) => {
      setNodes((current) => current.filter((node) => node.id !== nodeId));
      setEdges((current) => current.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
      setSelectedNodeId(null);
    },
    [setNodes, setEdges],
  );

  const saveMutation = useMutation({
    mutationFn: () => {
      const definition = flowToDefinition(
        workflowQuery.data?.name ?? "Untitled workflow",
        nodes,
        edges,
      );
      return updateWorkflowDraft(workspaceId as string, workflowId as string, definition);
    },
    onSuccess: (workflow) => {
      queryClient.setQueryData(["workflow", workspaceId, workflowId], workflow);
      notifications.show({ message: "Draft saved", color: "green" });
    },
  });

  const validateMutation = useMutation({
    mutationFn: async () => {
      await saveMutation.mutateAsync();
      return validateWorkflow(workspaceId as string, workflowId as string);
    },
    onSuccess: (result) => {
      setValidationErrors(result.errors);
      notifications.show({
        message: result.is_valid ? "Workflow is valid" : "Workflow has validation errors",
        color: result.is_valid ? "green" : "red",
      });
    },
  });

  const publishMutation = useMutation({
    mutationFn: async () => {
      await saveMutation.mutateAsync();
      return publishWorkflow(workspaceId as string, workflowId as string);
    },
    onSuccess: (version) => {
      queryClient.invalidateQueries({ queryKey: ["workflow", workspaceId, workflowId] });
      setValidationErrors(null);
      notifications.show({ message: `Published v${version.version}`, color: "green" });
    },
    onError: (error) => {
      if (error instanceof ApiError && Array.isArray(error.detail)) {
        setValidationErrors(error.detail as ValidationError[]);
      }
      notifications.show({ message: "Publish failed validation", color: "red" });
    },
  });

  const selectedNode = useMemo(
    () => nodes.find((node) => node.id === selectedNodeId) ?? null,
    [nodes, selectedNodeId],
  );

  if (!workspaceId || workflowQuery.isLoading) {
    return <Loader />;
  }

  if (!workflowQuery.data) {
    return <Text>Workflow not found.</Text>;
  }

  return (
    <Stack h="calc(100vh - 100px)" gap="xs">
      <Group justify="space-between">
        <Group gap="xs">
          <Text fw={600}>{workflowQuery.data.name}</Text>
          {workflowQuery.data.published_version ? (
            <Badge color="green">Published v{workflowQuery.data.published_version}</Badge>
          ) : (
            <Badge color="gray">Draft</Badge>
          )}
        </Group>
        <Group gap="xs">
          <Button size="sm" variant="light" loading={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
            Save draft
          </Button>
          <Button size="sm" variant="light" loading={validateMutation.isPending} onClick={() => validateMutation.mutate()}>
            Validate
          </Button>
          <Button size="sm" loading={publishMutation.isPending} onClick={() => publishMutation.mutate()}>
            Publish
          </Button>
        </Group>
      </Group>

      {validationErrors && validationErrors.length > 0 && (
        <Alert color="red" title="Validation errors">
          <Stack gap={2}>
            {validationErrors.map((error, index) => (
              <Text key={index} size="xs">
                [{error.code}] {error.message}
              </Text>
            ))}
          </Stack>
        </Alert>
      )}

      <Group gap={0} style={{ flex: 1, minHeight: 0 }} align="stretch">
        <NodePalette onAdd={addNode} />

        <div style={{ flex: 1, height: "100%" }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={{
              style: { stroke: "#868e96", strokeWidth: 1.5 },
              markerEnd: { type: MarkerType.ArrowClosed, color: "#868e96" },
            }}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            onPaneClick={() => setSelectedNodeId(null)}
            fitView
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>

        {selectedNode && (
          <NodeConfigPanel
            key={selectedNode.id}
            nodeId={selectedNode.id}
            nodeType={selectedNode.data.nodeType}
            config={selectedNode.data.config}
            onApply={applyNodeConfig}
            onDelete={deleteNode}
          />
        )}

        <TestRunPanel
          workspaceId={workspaceId}
          workflowId={workflowId as string}
          isPublished={Boolean(workflowQuery.data.published_version)}
        />
      </Group>
    </Stack>
  );
}
