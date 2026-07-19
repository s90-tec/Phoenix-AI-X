"""Reserved performance test tier; add benchmark baselines as features arrive."""

import pytest


@pytest.mark.performance
def test_performance_harness_is_discoverable() -> None:
    assert True

