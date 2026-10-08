from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MT5ConnectorError(RuntimeError):
    pass


class MT5Connector:
    """Functional MT5/MT4 connector with simulator fallback for local testing."""

    def __init__(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        path: Optional[str] = None,
        simulator: bool = True,
    ) -> None:
        self.login = settings.mt5_login if login is None else login
        self.password = settings.mt5_password if password is None else password
        self.server = settings.mt5_server if server is None else server
        self.path = settings.mt5_path if path is None else path
        self.simulator = simulator
        self._connected = False
        self._mt5 = None
        self._simulated_prices = {
            "EURUSD": 1.10250,
            "GBPUSD": 1.29580,
            "USDJPY": 157.280,
            "USDCHF": 0.89810,
            "AUDUSD": 0.66620,
            "NZDUSD": 0.61150,
        }
        logger.info(f"MT5Connector initialized (simulator={simulator})")

    def connect(self) -> bool:
        """Connect to MT4/MT5 or simulator."""
        if self.simulator:
            self._connected = True
            logger.info("Connected to simulator mode")
            return True

        try:
            import MetaTrader5 as mt5  # type: ignore
        except Exception as exc:
            logger.error(f"MetaTrader5 not available: {exc}")
            self._connected = False
            return False

        self._mt5 = mt5

        if self.login == 0:
            logger.warning("MT5_LOGIN is 0; cannot connect to live MT5")
            self._connected = False
            return False

        try:
            if self.path:
                initialize_kwargs = {
                    "path": self.path,
                    "login": self.login,
                    "password": self.password,
                    "server": self.server,
                }
            else:
                initialize_kwargs = {
                    "login": self.login,
                    "password": self.password,
                    "server": self.server,
                }

            if not mt5.initialize(**initialize_kwargs):
                logger.error(f"MT5 initialize failed")
                self._connected = False
                return False

            account = mt5.account_info()
            self._connected = account is not None
            if self._connected:
                logger.info(f"Connected to MT5 account {self.login}")
            else:
                logger.error(f"Failed to get account info")
                self.disconnect()
        except Exception as exc:
            logger.error(f"Connection error: {exc}")
            self._connected = False

        return self._connected

    def disconnect(self) -> None:
        """Disconnect from MT5."""
        if self._mt5 is not None:
            try:
                self._mt5.shutdown()
                logger.info("Disconnected from MT5")
            except Exception as exc:
                logger.warning(f"Error during disconnect: {exc}")
        self._connected = False
        self._mt5 = None

    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected

    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """Get current ask price for a symbol."""
        symbol = symbol.upper()
        if self.simulator:
            return self._simulated_prices.get(symbol)
        if self._mt5 is None:
            return None
        try:
            tick = self._mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            return float(tick.ask)
        except Exception as exc:
            logger.warning(f"Error fetching price for {symbol}: {exc}")
            return None

    def get_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """Get prices for multiple symbols."""
        symbols = list(symbols or self._simulated_prices.keys())
        result: Dict[str, float] = {}
        for symbol in symbols:
            price = self.get_symbol_price(symbol)
            if price is not None:
                result[symbol.upper()] = price
        return result

    def get_history(
        self, symbol: str, timeframe: str = "M1", count: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get OHLCV candle history."""
        symbol = symbol.upper()
        if self.simulator:
            import random
            base = self._simulated_prices.get(symbol, 1.0)
            candles: List[Dict[str, Any]] = []
            epoch = 1710000000
            for idx in range(count):
                base = base + (random.random() - 0.5) * 0.0008
                candles.append(
                    {
                        "time": epoch + idx * 60,
                        "open": round(base, 5),
                        "high": round(base + 0.0004, 5),
                        "low": round(base - 0.0004, 5),
                        "close": round(base + (random.random() - 0.5) * 0.0002, 5),
                        "tick_volume": 100,
                    }
                )
            return candles

        if self._mt5 is None:
            raise MT5ConnectorError("MetaTrader5 is not connected")

        tf_map = {
            "M1": self._mt5.TIMEFRAME_M1,
            "M5": self._mt5.TIMEFRAME_M5,
            "M15": self._mt5.TIMEFRAME_M15,
            "H1": self._mt5.TIMEFRAME_H1,
        }
        tf = tf_map.get(timeframe.upper(), self._mt5.TIMEFRAME_M1)
        try:
            rates = self._mt5.copy_rates_from_pos(symbol, tf, 0, count)
            if rates is None:
                return []
            return [dict(rate._asdict()) for rate in rates]
        except Exception as exc:
            logger.error(f"Error fetching history for {symbol}: {exc}")
            return []

    def place_order(
        self,
        symbol: str,
        action: str,
        volume: float = 0.01,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "AI signal",
    ) -> Dict[str, Any]:
        """Place a market order."""
        action = action.upper()
        if self.simulator:
            ticket = 100000 + abs(hash(f"{symbol}-{action}-{comment}") % 900000)
            order_result = {
                "status": "simulated",
                "ticket": ticket,
                "symbol": symbol.upper(),
                "action": action,
                "volume": float(volume),
                "price": float(price) if price is not None else self.get_symbol_price(symbol),
                "sl": float(sl) if sl is not None else None,
                "tp": float(tp) if tp is not None else None,
                "comment": comment,
            }
            logger.info(f"Simulated order: {order_result}")
            return order_result

        if self._mt5 is None:
            raise MT5ConnectorError("MetaTrader5 is not connected")

        if action not in {"BUY", "SELL"}:
            raise MT5ConnectorError("Action must be BUY or SELL")

        try:
            import MetaTrader5 as mt5  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise MT5ConnectorError(f"MetaTrader5 unavailable: {exc}") from exc

        current_price = price if price is not None else self.get_symbol_price(symbol)
        if current_price is None:
            raise MT5ConnectorError(f"Cannot get price for {symbol}")

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol.upper(),
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
            "price": float(current_price),
            "sl": float(sl) if sl is not None else 0.0,
            "tp": float(tp) if tp is not None else 0.0,
            "deviation": 10,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
            "comment": comment,
        }
        try:
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise MT5ConnectorError(f"Order failed: {result.comment}")
            logger.info(f"Order placed: {result}")
            return result._asdict()
        except Exception as exc:
            logger.error(f"Error placing order: {exc}")
            raise MT5ConnectorError(f"Failed to place order: {exc}") from exc


__all__ = ["MT5Connector", "MT5ConnectorError"]
