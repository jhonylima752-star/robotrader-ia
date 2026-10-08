from __future__ import annotations

from app.config import settings


class SignalEngine:
    def __init__(self, confidence_threshold: float | None = None):
        self.confidence_threshold = confidence_threshold or settings.signal_confidence_threshold
        self.lead_seconds = settings.forecast_horizon_seconds

    def choose_best_pair(self, predictions: dict[str, float], fallback_symbol: str = "EURUSD") -> tuple[str, float]:
        if not predictions:
            return fallback_symbol, 0.0
        return max(predictions.items(), key=lambda item: item[1])

    def build_signal(self, symbol: str, probability: float, current_price: float):
        side = "BUY" if probability >= self.confidence_threshold else "SELL"
        if side == "BUY":
            entry = current_price
            sl = current_price * (1 - 0.0015)
            tp = current_price * (1 + 0.0030)
        else:
            entry = current_price
            sl = current_price * (1 + 0.0015)
            tp = current_price * (1 - 0.0030)

        return {
            "symbol": symbol,
            "side": side,
            "entry": round(entry, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "confidence": round(probability, 4),
            "lead_seconds": self.lead_seconds,
            "timestamp": "now",
        }
