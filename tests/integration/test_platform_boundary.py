"""Integration-tier placeholder for future service-backed adapter checks."""

import pytest


@pytest.mark.integration
def test_platform_package_is_importable() -> None:
    import phoenix_ai

    assert phoenix_ai.__version__ == "0.1.0"

