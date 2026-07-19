from __future__ import annotations

from typing import Any, Callable, Optional

from app.development.model_registry import ModelRecord


class EvaluationPipeline:
    """Coordinate the validation stages for a candidate model."""

    def __init__(
        self,
        *,
        unit_test_runner: Optional[Callable[[], dict[str, Any]]] = None,
        integration_test_runner: Optional[Callable[[], dict[str, Any]]] = None,
        backtest_runner: Optional[Callable[[ModelRecord], dict[str, Any]]] = None,
    ) -> None:
        self.unit_test_runner = unit_test_runner or self._default_unit_tests
        self.integration_test_runner = integration_test_runner or self._default_integration_tests
        self.backtest_runner = backtest_runner or self._default_backtest

    def evaluate(self, model: ModelRecord) -> dict[str, Any]:
        unit_result = self.unit_test_runner()
        integration_result = self.integration_test_runner()
        backtest_result = self.backtest_runner(model)
        passed = bool(unit_result.get("passed", False) and integration_result.get("passed", False) and backtest_result.get("passed", False))
        return {
            "model_version": model.version,
            "unit_tests": unit_result,
            "integration_tests": integration_result,
            "backtest": backtest_result,
            "passed": passed,
        }

    def _default_unit_tests(self) -> dict[str, Any]:
        return {"passed": True, "details": "No unit tests configured"}

    def _default_integration_tests(self) -> dict[str, Any]:
        return {"passed": True, "details": "No integration tests configured"}

    def _default_backtest(self, model: ModelRecord) -> dict[str, Any]:
        return {"passed": True, "metrics": model.backtest_metrics}
