"""Pluggable parameter search implementations."""

from __future__ import annotations

from itertools import product
from random import Random
from typing import Any, Callable


Objective = Callable[[dict[str, Any]], float]


class ParameterOptimizer:
    """Searches parameter spaces through deterministic grid/random interfaces.

    Bayesian and genetic modes expose stable extension points until dedicated
    optimizers are configured.
    """

    def __init__(self, objective: Objective | None = None, seed: int = 7) -> None:
        self.objective = objective or self._default_objective
        self._random = Random(seed)

    def optimize(self, parameter_space: dict[str, list[Any]], *, mode: str = "grid", iterations: int = 20) -> dict[str, Any]:
        if not parameter_space:
            raise ValueError("parameter_space cannot be empty")
        normalized = mode.lower()
        if normalized not in {"grid", "random", "bayesian", "genetic"}:
            raise ValueError(f"Unsupported optimization mode: {mode}")
        combinations = self._grid(parameter_space)
        if normalized == "random":
            combinations = [self._random.choice(combinations) for _ in range(min(iterations, max(1, len(combinations))))]
        # Bayesian/genetic are intentionally protocol-compatible fallbacks until
        # specialised backends are injected.
        if normalized in {"bayesian", "genetic"}:
            combinations = combinations[:max(1, min(iterations, len(combinations)))]
        scored = [(params, float(self.objective(params))) for params in combinations]
        best_params, best_score = max(scored, key=lambda result: result[1])
        return {"mode": normalized, "best_params": best_params, "best_score": best_score, "evaluations": len(scored)}

    @staticmethod
    def _grid(space: dict[str, list[Any]]) -> list[dict[str, Any]]:
        keys, values = list(space), list(space.values())
        if any(not options for options in values):
            raise ValueError("Every parameter needs at least one candidate value")
        return [dict(zip(keys, candidate)) for candidate in product(*values)]

    @staticmethod
    def _default_objective(params: dict[str, Any]) -> float:
        return sum(float(value) for value in params.values() if isinstance(value, (int, float)))
