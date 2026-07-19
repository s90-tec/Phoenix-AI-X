from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class ModelRecord:
    """Metadata container for every model candidate and production artifact."""

    version: str
    artifact_path: str
    training_data_range: tuple[str, str]
    hyperparameters: dict[str, Any]
    validation_metrics: dict[str, float]
    backtest_metrics: dict[str, float]
    deployment_status: str = "candidate"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    experiment_branch: Optional[str] = None
    report_path: Optional[str] = None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


class ModelRegistry:
    """Manage model lifecycle with promotion and archival safeguards."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or Path.cwd() / "models" / "registry")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, ModelRecord] = {}
        self._production_version: Optional[str] = None

    def register_model(
        self,
        *,
        version: str,
        artifact_path: str,
        training_data_range: tuple[str, str],
        hyperparameters: dict[str, Any],
        validation_metrics: dict[str, float],
        backtest_metrics: dict[str, float],
        deployment_status: str = "candidate",
    ) -> ModelRecord:
        record = ModelRecord(
            version=version,
            artifact_path=artifact_path,
            training_data_range=training_data_range,
            hyperparameters=hyperparameters,
            validation_metrics=validation_metrics,
            backtest_metrics=backtest_metrics,
            deployment_status=deployment_status,
        )
        self._records[version] = record
        if deployment_status == "production":
            self._production_version = version
        self._persist(record)
        return record

    def get_model(self, version: str) -> ModelRecord:
        if version not in self._records:
            self._load_from_disk(version)
        if version not in self._records:
            raise KeyError(f"Unknown model version: {version}")
        return self._records[version]

    def list_models(self) -> list[ModelRecord]:
        return [self.get_model(version) for version in sorted(self._records)]

    def promote_model(self, version: str) -> ModelRecord:
        candidate = self.get_model(version)
        if self._production_version and self._production_version != version:
            previous_production = self.get_model(self._production_version)
            previous_production.deployment_status = "archived"
            self._persist(previous_production)
        candidate.deployment_status = "production"
        self._production_version = version
        self._persist(candidate)
        return candidate

    def archive_model(self, version: str) -> ModelRecord:
        record = self.get_model(version)
        record.deployment_status = "archived"
        self._persist(record)
        return record

    def _persist(self, record: ModelRecord) -> None:
        path = self.storage_dir / f"{record.version}.json"
        path.write_text(json.dumps(record.to_payload(), indent=2), encoding="utf-8")

    def _load_from_disk(self, version: str) -> None:
        path = self.storage_dir / f"{version}.json"
        if not path.exists():
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._records[version] = ModelRecord(**payload)
