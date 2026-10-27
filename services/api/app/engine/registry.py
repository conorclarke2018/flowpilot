TRIGGER_NODE_TYPES = frozenset({"trigger.manual", "trigger.webhook"})

NODE_TYPES = frozenset(
    TRIGGER_NODE_TYPES
    | {
        "data.transform",
        "ai.classify",
        "logic.condition",
        "human.approval",
        "action.mock_email",
        "action.webhook",
    }
)

NODES_WITH_SIDE_EFFECTS = frozenset({"action.mock_email", "action.webhook"})
