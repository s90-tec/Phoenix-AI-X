"""Pure business concepts. This layer never imports frameworks or infrastructure."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ExperimentStatus(StrEnum):
    """Lifecycle states for a research experiment."""

    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ResearchExperiment:
    """A framework-independent representation of an experiment."""

    name: str
    hypothesis: str
    id: UUID = field(default_factory=uuid4)
    status: ExperimentStatus = ExperimentStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)

