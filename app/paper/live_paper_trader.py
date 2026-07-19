import logging
from typing import Optional

import ccxt

from app.ai.predictor import Predictor
from app.config import config
from app.database import create_database
from app.database.repository import TradeRepository
from app.data.realtime_features import FeatureEngine
from app.exchange.market_data import MarketData
from app.paper.live_runner import LiveRunner
from app.paper.trader import PaperTrader as ExecutionTrader
from app.portfolio.portfolio import Portfolio
from app.risk.risk_manager import RiskManager

logger = logging.getLogger(__name__)


class PaperTrader:
    """Minimal compatibility wrapper that preserves the original live entry-point behavior."""

    def __init__(
        self,
        symbol: str = config.SYMBOL,
        timeframe: str = config.TIMEFRAME,
        limit: int = config.FETCH_LIMIT,
        poll_interval: int = config.LOOP_INTERVAL,
        error_sleep: int = config.LOOP_INTERVAL,
        exchange: Optional[ccxt.Exchange] = None,
        portfolio: Optional[Portfolio] = None,
        db_engine: Optional[object] = None,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.poll_interval = poll_interval
        self.error_sleep = error_sleep
        self.exchange = exchange or ccxt.binance()
        self.portfolio = portfolio or Portfolio()
        self.db_engine = db_engine or create_database("phoenix_trades.db")
        self.repository = TradeRepository(self.db_engine)
        self.market_data = MarketData(exchange=self.exchange)
        self.feature_engine = FeatureEngine(exchange=self.exchange)
        self.predictor = Predictor()
        self.risk_manager = RiskManager()
        self.execution_trader = ExecutionTrader(
            portfolio=self.portfolio,
            repository=self.repository,
            risk_manager=self.risk_manager,
            logger_instance=logger,
        )
        self.runner = LiveRunner(
            market_data=self.market_data,
            feature_engine=self.feature_engine,
            predictor=self.predictor,
            risk_manager=self.risk_manager,
            trader=self.execution_trader,
            logger_instance=logger,
            config_module=type(
                "Config",
                (),
                {
                    "SYMBOL": self.symbol,
                    "TIMEFRAME": self.timeframe,
                    "FETCH_LIMIT": self.limit,
                    "LOOP_INTERVAL": self.poll_interval,
                    "MAX_RETRIES": config.MAX_RETRIES,
                    "MIN_CONFIDENCE": config.MIN_CONFIDENCE,
                },
            )(),
        )

    def _fetch_ohlcv(self):
        return self.market_data.fetch_candles(
            symbol=self.symbol,
            timeframe=self.timeframe,
            limit=self.limit,
            retries=config.MAX_RETRIES,
        )

    def _get_signal(self, feature_row):
        return self.predictor.predict_signal(feature_row)

    def step(self) -> None:
        candles = self._fetch_ohlcv()
        feature_row = self.feature_engine.get_latest_feature_row(limit=len(candles))
        signal, confidence = self._get_signal(feature_row)

        if confidence < config.MIN_CONFIDENCE:
            return

        validated_signal = self.risk_manager.manage_risk(signal, confidence, candles.iloc[-1]["close"])
        if validated_signal == "HOLD":
            return

        self.execution_trader.execute(
            signal=validated_signal,
            price=float(candles.iloc[-1]["close"]),
            confidence=confidence,
            symbol=self.symbol,
        )

    def run(self) -> None:
        self.runner.run()


if __name__ == "__main__":
    trader = PaperTrader()
    trader.run()
