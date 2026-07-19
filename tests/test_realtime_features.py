import unittest
from unittest.mock import patch

import pandas as pd

from app.data.realtime_features import FeatureEngine, get_latest_features
from app.ai.predictor import FEATURES


class RealtimeFeaturesTests(unittest.TestCase):
    def test_feature_engine_builds_valid_vector(self) -> None:
        engine = FeatureEngine(exchange=object())

        candles = pd.DataFrame(
            {
                "timestamp": [1, 2, 3, 4, 5],
                "open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "high": [101.0, 102.0, 103.0, 104.0, 105.0],
                "low": [99.0, 100.0, 101.0, 102.0, 103.0],
                "close": [100.0, 101.0, 102.0, 103.0, 104.0],
                "volume": [10.0, 12.0, 13.0, 14.0, 15.0],
            }
        )

        with patch.object(engine, "_fetch_candles", return_value=candles):
            features = engine.get_latest_feature_row(limit=5)

        self.assertFalse(features.empty)
        self.assertEqual(list(features.columns), FEATURES)
        self.assertFalse(features.isna().any().any())

    def test_get_latest_features_returns_single_row(self) -> None:
        with patch("app.data.realtime_features.FeatureEngine.get_latest_feature_row") as mock_row:
            mock_row.return_value = pd.DataFrame({"EMA20": [1.0]})
            result = get_latest_features()

        self.assertEqual(result.shape[0], 1)


if __name__ == "__main__":
    unittest.main()
