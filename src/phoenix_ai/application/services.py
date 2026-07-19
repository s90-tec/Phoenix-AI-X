"""Use cases that orchestrate domain objects through injected ports."""

from dataclasses import dataclass

from phoenix_ai.domain.entities import ResearchExperiment
from phoenix_ai.domain.ports import ExperimentRepository


@dataclass(slots=True)
class CreateExperiment:
    """Application service placeholder for experiment registration."""

    repository: ExperimentRepository

    def execute(self, *, name: str, hypothesis: str) -> ResearchExperiment:
        experiment = ResearchExperiment(name=name, hypothesis=hypothesis)
        self.repository.add(experiment)
        return experiment

