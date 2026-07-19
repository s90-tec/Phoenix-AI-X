"""Smoke tests for clean-architecture wiring."""

from phoenix_ai.bootstrap import build_container


def test_container_creates_experiment() -> None:
    container = build_container()
    experiment = container.create_experiment.execute(name="baseline", hypothesis="placeholder")
    assert experiment.name == "baseline"

