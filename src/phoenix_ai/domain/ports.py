"""Dependency inversion contracts implemented by infrastructure adapters."""

from collections.abc import Iterable
from typing import Protocol

from phoenix_ai.domain.entities import ResearchExperiment


class ExperimentRepository(Protocol):
    """Persistence port owned by the domain/application boundary."""

    def add(self, experiment: ResearchExperiment) -> None: ...

    def list(self) -> Iterable[ResearchExperiment]: ...

