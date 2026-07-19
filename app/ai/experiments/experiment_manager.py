from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, List

from app.ai.experiments.experiment import Experiment


class ExperimentManager:
    """Create and update experiments while persisting them to disk."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or Path("experiments"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._experiments: Dict[str, Experiment] = {}

    def create_experiment(self, experiment_id: str, **kwargs: Any) -> Experiment:
        if experiment_id in self._experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")
        experiment = Experiment(experiment_id=experiment_id, **kwargs)
        self._experiments[experiment_id] = experiment
        self._save(experiment)
        return experiment

    def update_status(self, experiment_id: str, status: str) -> Experiment:
        experiment = self.get(experiment_id)
        experiment.status = status
        self._save(experiment)
        return experiment

    def get(self, experiment_id: str) -> Experiment:
        if experiment_id not in self._experiments:
            path = self.storage_dir / f"{experiment_id}.json"
            if not path.exists():
                raise KeyError(f"Unknown experiment: {experiment_id}")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self._experiments[experiment_id] = Experiment(**payload)
        return self._experiments[experiment_id]

    def list(self) -> List[Experiment]:
        return list(self._experiments.values())

    def _save(self, experiment: Experiment) -> None:
        path = self.storage_dir / f"{experiment.experiment_id}.json"
        path.write_text(json.dumps(experiment.__dict__, indent=2), encoding="utf-8")
