from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class AutoRetrainingScheduler:
    """Simple scheduler that decides whether retraining is due."""

    interval_minutes: int = 60
    last_run_at: datetime | None = None

    def should_run(self, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(timezone.utc)
        if self.last_run_at is None:
            return True
        return current_time - self.last_run_at >= timedelta(minutes=self.interval_minutes)

    def mark_run(self, now: datetime | None = None) -> None:
        self.last_run_at = now or datetime.now(timezone.utc)
