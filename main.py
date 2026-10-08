from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from app.config import settings
from app.data.loader import generate_synthetic_history, build_features
from app.models.forecast_model import train_model_for_symbol, prepare_dataset
from app.signals.signal_engine import SignalEngine
from app.mt_connector import MT5Connector
from app.alerts.telegram_alert import TelegramNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_trading() -> dict:
    """Run a complete trading simulation with MT5 connector."""
    logger.info("Starting trading simulation...")
    
    connector = MT5Connector(simulator=True)
    if not connector.connect():
        logger.error("Failed to connect to MT5")
        return {"status": "error", "message": "Connection failed"}

    prices = connector.get_prices(settings.symbols)
    logger.info(f"Current prices: {prices}")

    predictions = {}
    for symbol in settings.symbols:
        df = generate_synthetic_history(symbol=symbol, rows=500)
        X, y = prepare_dataset(df, horizon=5)
        if len(X) > 0:
            from sklearn.ensemble import RandomForestClassifier
            clf = RandomForestClassifier(n_estimators=50, random_state=42)
            clf.fit(X.iloc[:-50], y.iloc[:-50])
            if len(X) > 0:
                proba = clf.predict_proba(X.iloc[-1:])[:, 1][0]
                predictions[symbol] = float(proba)
                logger.info(f"{symbol}: {proba:.4f}")

    engine = SignalEngine()
    best_symbol, best_score = engine.choose_best_pair(predictions)
    logger.info(f"Best symbol: {best_symbol} ({best_score:.4f})")

    current_price = prices.get(best_symbol, 1.0)
    signal = engine.build_signal(best_symbol, best_score, current_price)
    logger.info(f"Signal: {signal}")

    order = connector.place_order(
        symbol=signal["symbol"],
        action=signal["side"],
        volume=settings.default_volume,
        price=signal["entry"],
        sl=signal["sl"],
        tp=signal["tp"],
        comment="AI FOREX robot signal",
    )
    logger.info(f"Order result: {order}")

    connector.disconnect()

    return {
        "status": "success",
        "connected": connector.is_connected(),
        "prices": prices,
        "predictions": predictions,
        "signal": signal,
        "order": order,
    }


def backtest_mode(data_dir: Path) -> dict:
    """Run backtest on historical data."""
    logger.info("Starting backtest...")
    data_dir.mkdir(parents=True, exist_ok=True)
    history_map = {}

    for symbol in settings.symbols:
        csv_path = data_dir / f"{symbol.lower()}.csv"
        if not csv_path.exists():
            df = generate_synthetic_history(symbol=symbol, rows=2000)
            df.to_csv(csv_path, index=False)
        history_map[symbol] = pd.read_csv(csv_path)

    results = {}
    for symbol, frame in history_map.items():
        metrics = train_model_for_symbol(frame, symbol=symbol, horizon=5)
        results[symbol] = metrics
        logger.info(f"{symbol}: accuracy={metrics['accuracy']:.4f}")

    return {"status": "success", "backtest_results": results}


def scan_mode() -> dict:
    """Scan symbols and generate signal."""
    logger.info("Starting scan mode...")
    return simulate_trading()


def status_mode() -> dict:
    """Check system status."""
    logger.info("Checking status...")
    connector = MT5Connector(simulator=settings.use_simulator)
    connected = connector.connect()

    return {
        "status": "ok",
        "simulator": settings.use_simulator,
        "mt5_connected": connected,
        "symbols": settings.symbols,
        "forecast_horizon_seconds": settings.forecast_horizon_seconds,
        "confidence_threshold": settings.signal_confidence_threshold,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI FOREX Robot Trader")
    parser.add_argument(
        "--mode",
        choices=["simulate", "scan", "backtest", "status"],
        default="status",
    )
    parser.add_argument("--data-dir", type=Path, default=settings.data_dir)
    args = parser.parse_args()

    output = None
    if args.mode == "simulate":
        output = simulate_trading()
    elif args.mode == "scan":
        output = scan_mode()
    elif args.mode == "backtest":
        output = backtest_mode(args.data_dir)
    elif args.mode == "status":
        output = status_mode()

    print(json.dumps(output, indent=2, default=str))
