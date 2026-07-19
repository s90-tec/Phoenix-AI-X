from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.config import config
from app.ai.predictor import Predictor
from app.data.realtime_features import FeatureEngine
from app.exchange.market_data import MarketData
from app.paper.trader import PaperTrader
from app.risk.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class LiveRunner:
    """Coordinate the live trading workflow using injected collaborators."""

    def __init__(
        self,
        market_data: MarketData,
        feature_engine: FeatureEngine,
        predictor: Predictor,
        risk_manager: RiskManager,
        trader: PaperTrader,
        logger_instance: Optional[logging.Logger] = None,
        config_module: Optional[Any] = None,
    ) -> None:
        self.market_data = market_data
        self.feature_engine = feature_engine
        self.predictor = predictor
        self.risk_manager = risk_manager
        self.trader = trader
        self.logger = logger_instance or logger
        self.config_module = config_module or config

    def run_once(self) -> None:
        """Run one complete trading iteration."""
        candles = self.market_data.fetch_candles(
            symbol=self.config_module.SYMBOL,
            timeframe=self.config_module.TIMEFRAME,
            limit=self.config_module.FETCH_LIMIT,
            retries=self.config_module.MAX_RETRIES,
        )
        feature_row = self.feature_engine.get_latest_feature_row(limit=len(candles))
        signal, confidence = self.predictor.predict_signal(feature_row)

        self.logger.info(
            "Prediction received",
            extra={"signal": signal, "confidence": confidence, "symbol": self.config_module.SYMBOL},
        )

        if confidence < self.config_module.MIN_CONFIDENCE:
            self.logger.info("Confidence below minimum threshold; skipping execution")
            return

        validated_signal = self.risk_manager.manage_risk(signal, confidence, candles.iloc[-1]["close"])
        self.logger.info(
            "Signal validated",
            extra={"signal": validated_signal, "confidence": confidence},
        )

        if validated_signal == "HOLD":
            self.logger.info("HOLD signal received; skipping execution")
            return

        self.trader.execute(
            signal=validated_signal,
            price=float(candles.iloc[-1]["close"]),
            confidence=confidence,
            symbol=self.config_module.SYMBOL,
        )

    def run(self) -> None:
        """Run the orchestration loop until interrupted."""
        self.logger.info("Live runner starting", extra={"symbol": self.config_module.SYMBOL})
        try:
            while True:
                try:
                    self.run_once()
                except KeyboardInterrupt:
                    self.logger.info("Shutdown requested")
                    break
                except Exception as exc:  # pragma: no cover - runtime resilience
                    self.logger.exception("Transient error in live runner: %s", exc)
                time.sleep(self.config_module.LOOP_INTERVAL)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")

    def shutdown(self) -> None:
        """Log shutdown for clean exit."""
        self.logger.info("Live runner shutting down")
