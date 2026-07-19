import unittest

from app.strategy.base import BaseStrategy
from app.strategy.registry import StrategyRegistry


class DummyStrategy(BaseStrategy):
    name = "dummy"

    def generate_signal(self, features):
        return None


class StrategyRegistryTests(unittest.TestCase):
    def test_register_and_list(self) -> None:
        registry = StrategyRegistry()
        registry.register(DummyStrategy)
        self.assertIn("dummy", registry.list())

    def test_duplicate_registration_raises(self) -> None:
        registry = StrategyRegistry()
        registry.register(DummyStrategy)
        with self.assertRaises(ValueError):
            registry.register(DummyStrategy)


if __name__ == "__main__":
    unittest.main()
