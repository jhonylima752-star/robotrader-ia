from __future__ import annotations

from pathlib import Path

try:
    import MetaTrader5 as mt5
except Exception:
    mt5 = None


class MT5Bridge:
    def __init__(self, login: int = 0, password: str = "", server: str = ""):
        self.login = login
        self.password = password
        self.server = server
        self._connected = False
        self._client = None

    def connect(self):
        if mt5 is None:
            return False
        if self.login == 0:
            return False
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            return False
        self._client = mt5
        self._connected = True
        return True

    def disconnect(self):
        if mt5 is not None and self._connected:
            mt5.shutdown()
            self._connected = False

    def get_symbol_candles(self, symbol: str, timeframe: str = "M1", count: int = 1000):
        if not self._connected or mt5 is None:
            return []

        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
        }
        tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)
        return mt5.copy_rates_from_pos(symbol, tf, 0, count)

    def send_alert(self, symbol: str, side: str, entry: float, sl: float, tp: float, lead_seconds: int):
        if not self._connected or mt5 is None:
            return False

        message = (
            f"AI Signal | {symbol} | {side} | Entry={entry:.5f} | "
            f"SL={sl:.5f} | TP={tp:.5f} | Lead={lead_seconds}s"
        )
        mt5.log_write(message)
        return True
