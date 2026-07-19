import unittest

from app.strategy.loader import StrategyLoader
from app.strategy.registry import StrategyRegistry


class StrategyLoaderTests(unittest.TestCase):
    def test_loader_discovers_strategies(self) -> None:
        registry = StrategyRegistry()
        loader = StrategyLoader(registry)
        discovered = loader.discover()
        self.assertGreaterEqual(len(discovered), 1)
        self.assertIn("trend_following", registry.list())


if __name__ == "__main__":
    unittest.main()
