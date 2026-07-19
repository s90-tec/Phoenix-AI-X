import unittest

from app.strategy.factory import StrategyFactory
from app.strategy.registry import StrategyRegistry
from app.strategy.strategies.trend_following import TrendFollowingStrategy


class StrategyFactoryTests(unittest.TestCase):
    def test_factory_creates_registered_strategy(self) -> None:
        registry = StrategyRegistry()
        registry.register(TrendFollowingStrategy)
        factory = StrategyFactory(registry)
        strategy = factory.create("trend_following")
        self.assertEqual(strategy.name, "trend_following")


if __name__ == "__main__":
    unittest.main()
