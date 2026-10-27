from typing import Any


class ExecutionContext:
    """Holds per-node outputs for a single run, used to resolve data references."""

    def __init__(self, trigger_input: dict[str, Any]) -> None:
        self.trigger_input = trigger_input
        self._node_outputs: dict[str, dict[str, Any]] = {}

    def set_output(self, node_id: str, output: dict[str, Any]) -> None:
        self._node_outputs[node_id] = output

    def resolve(self, value: Any) -> Any:
        """Recursively resolve `$.<node_id>.<path>` string references inside config values."""
        if isinstance(value, str) and value.startswith("$."):
            return self._resolve_path(value[2:])
        if isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.resolve(v) for v in value]
        return value

    def _resolve_path(self, path: str) -> Any:
        parts = path.split(".")
        root, *rest = parts
        if root == "trigger":
            current: Any = self.trigger_input
        else:
            current = self._node_outputs.get(root, {})
        for part in rest:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
        return current
