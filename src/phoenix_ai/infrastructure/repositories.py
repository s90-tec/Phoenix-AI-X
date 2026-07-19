"""Infrastructure adapters. Replace the in-memory adapter with SQLAlchemy when needed."""

from collections.abc import Iterable

from phoenix_ai.domain.entities import ResearchExperiment


class InMemoryExperimentRepository:
    """Development-only repository illustrating the Repository pattern."""

    def __init__(self) -> None:
        self._items: list[ResearchExperiment] = []

    def add(self, experiment: ResearchExperiment) -> None:
        self._items.append(experiment)

    def list(self) -> Iterable[ResearchExperiment]:
        return tuple(self._items)

