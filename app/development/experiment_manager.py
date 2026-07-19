from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Experiment:
    version: str
    branch_name: str
    report_path: str
    baseline_version: str
    hyperparameters: dict[str, Any]
    created_at: str


class ExperimentManager:
    """Create branch-style experiments and write detailed evaluation reports."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir or Path.cwd() / "experiments")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.storage_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment(self, candidate_version: str, baseline_version: str, hyperparameters: dict[str, Any]) -> Experiment:
        branch_name = f"exp/{candidate_version}"
        report_path = self.reports_dir / f"{candidate_version}.json"
        created_at = datetime.now(timezone.utc).isoformat()
        experiment = Experiment(
            version=candidate_version,
            branch_name=branch_name,
            report_path=str(report_path),
            baseline_version=baseline_version,
            hyperparameters=hyperparameters,
            created_at=created_at,
        )
        report_payload = {
            "version": candidate_version,
            "branch_name": branch_name,
            "baseline_version": baseline_version,
            "hyperparameters": hyperparameters,
            "created_at": created_at,
            "summary": "Pending evaluation",
        }
        report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        return experiment

    def write_report(self, experiment: Experiment, payload: dict[str, Any]) -> str:
        report_path = Path(experiment.report_path)
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(report_path)
