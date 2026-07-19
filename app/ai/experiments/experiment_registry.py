from __future__ import annotations

from typing import Any, Dict, List


class ExperimentRegistry:
    """Registry that stores experiments without overwriting existing ones."""

    def __init__(self) -> None:
        self._experiments: Dict[str, Dict[str, Any]] = {}

    def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        experiment_id = payload.get("id") or payload.get("experiment_id")
        if not experiment_id:
            raise ValueError("Experiment id is required")
        if experiment_id in self._experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")
        self._experiments[experiment_id] = payload
        return payload

    def get(self, experiment_id: str) -> Dict[str, Any]:
        return self._experiments[experiment_id]

    def list(self) -> List[Dict[str, Any]]:
        return list(self._experiments.values())
