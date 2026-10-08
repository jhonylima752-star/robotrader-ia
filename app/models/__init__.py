from pathlib import Path
import math
import pandas as pd


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close", "volume"}
    lower = {col.lower(): col for col in df.columns}
    normalized = df.rename(columns={old: new for new, old in lower.items()})
    for col in required:
        if col not in normalized.columns:
            raise ValueError(f"Missing required column: {col}")
    normalized = normalized.sort_values("timestamp").reset_index(drop=True)
    return normalized


def load_csv_history(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Market history file not found: {path}")

    df = pd.read_csv(path)
    normalized = _ensure_columns(df)
    return normalized


def generate_synthetic_history(symbol: str, rows: int = 2500, seed: int = 42) -> pd.DataFrame:
    import numpy as np

    rng = np.random.default_rng(seed)
    base = 1.1000
    drift = rng.normal(0.0, 0.00005, rows)
    values = np.cumsum(drift) + base

    timestamps = pd.date_range("2024-01-01", periods=rows, freq="min")
    opens = values.copy()
    closes = values + rng.normal(0.0, 0.00015, rows)
    highs = np.maximum(opens, closes) + rng.uniform(0.0001, 0.0006, rows)
    lows = np.minimum(opens, closes) - rng.uniform(0.0001, 0.0006, rows)
    volumes = rng.integers(100, 500, rows)

    data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
    )
    data["symbol"] = symbol
    return data


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame["ret_1m"] = frame["close"].pct_change(1).fillna(0.0)
    frame["ret_5m"] = frame["close"].pct_change(5).fillna(0.0)
    frame["ret_15m"] = frame["close"].pct_change(15).fillna(0.0)
    frame["sma_fast"] = frame["close"].rolling(10).mean()
    frame["sma_slow"] = frame["close"].rolling(30).mean()
    frame["spread"] = frame["close"] - frame["sma_fast"]
    frame["volatility"] = frame["close"].pct_change().rolling(20).std().fillna(0.0)
    frame["rsi"] = _rsi(frame["close"], periods=14)
    frame["momentum"] = frame["close"] - frame["close"].shift(10)
    frame["atr"] = (frame["high"] - frame["low"]).rolling(14).mean().fillna(0.0)
    frame["feature_score"] = frame["ret_1m"] + frame["ret_5m"] + frame["spread"] / frame["close"]
    return frame


def _rsi(series: pd.Series, periods: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.rolling(window=periods, min_periods=1).mean()
    avg_loss = down.rolling(window=periods, min_periods=1).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def discover_symbol_files(data_dir: str | Path):
    path = Path(data_dir)
    if not path.exists():
        return []
    return sorted(path.glob("*.csv"))
