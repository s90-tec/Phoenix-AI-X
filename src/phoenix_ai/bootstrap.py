"""Composition root: dependency injection is configured only at the edge."""

from dataclasses import dataclass

from phoenix_ai.application.services import CreateExperiment
from phoenix_ai.infrastructure.repositories import InMemoryExperimentRepository


@dataclass(frozen=True, slots=True)
class Container:
    """Small explicit DI container; evolve to a provider library only if needed."""

    create_experiment: CreateExperiment


def build_container() -> Container:
    """Wire application services to their infrastructure implementations."""
    return Container(create_experiment=CreateExperiment(InMemoryExperimentRepository()))

