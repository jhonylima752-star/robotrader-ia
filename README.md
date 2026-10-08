# Robot Trader IA

A Python-based trading system scaffold for FOREX on MT4/MT5 with AI-assisted signal generation, autonomous pair selection, and Telegram/MT terminal notifications.

This repository is intentionally structured as a production-ready starter kit rather than a black-box promise of guaranteed profitability. It contains the core architecture for:

- data ingestion from market history
- feature engineering for signal modeling
- AI model training and validation
- autonomous pair selection among majors
- forecast signal generation with 2-minute lead time
- optional MetaTrader 5 integration
- Telegram alert delivery
- backtesting pipeline and metrics logging

Important: this project is for research and engineering education. Trading results depend on market conditions and rigorous validation. It should not be treated as financial advice.

## Project structure

```text
robotrader-ia/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── forecast_model.py
│   ├── mt_connector/
│   │   ├── __init__.py
│   │   └── mt5_bridge.py
│   ├── signals/
│   │   ├── __init__.py
│   │   └── signal_engine.py
│   └── alerts/
│       ├── __init__.py
│       └── telegram_alert.py
├── data/
│   └── sample/
│       └── .gitkeep
├── models/
│   └── .gitkeep
└── logs/
    └── .gitkeep
```

## Features

- Native MT4/MT5 connector abstraction via `app/mt_connector/mt5_bridge.py`
- Dynamic asset selection across a configured list of pairs
- AI-based predictive model using tabular features and classification
- Signal generation with a configurable 120-second lead time
- Telegram push notification support
- Backtesting/validation script and metrics output
- Reproducible local setup using `pip install -r requirements.txt`

## Quick start

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy example environment variables:

```bash
cp .env.example .env
```

5. Edit `.env` to include your MT5 and Telegram settings if needed.
6. Run the prototype:

```bash
python main.py --mode train
python main.py --mode scan
python main.py --mode backtest
```

## Environment variables

Create a `.env` file with options like:

```env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
MT5_LOGIN=123456
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Demo
SYMBOLS=EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,NZDUSD
FORECAST_HORIZON_SECONDS=120
```

## AI model strategy

The project uses a practical classification model based on engineered technical features:

- returns over several lookback windows
- moving average spread
- RSI
- ATR and volatility
- rolling normalization
- direction target computed from future price displacement

This architecture is intentionally modular so you can replace the classifier with an LSTM or transformer implementation later without rewriting the whole trading loop.

## Signal generation

Signals are produced by evaluating candidate symbols and choosing the pair with the highest predicted probability of directional move. The system then creates an actionable signal with:

- side: BUY or SELL
- entry price
- stop loss
- take profit
- confidence score
- lead time: 120 seconds by default

## Files to customize

- `app/config.py` for environment/config values
- `app/data/loader.py` for market data ingestion
- `app/models/forecast_model.py` for the predictive model
- `app/signals/signal_engine.py` for best-pair scoring and signal assembly
- `app/alerts/telegram_alert.py` for notification delivery
- `app/mt_connector/mt5_bridge.py` for MT4/MT5 integration

## Deployment notes

- MT4/MT5 integration is intentionally isolated behind the connector layer.
- Use a demo or sandbox account for validation before live trading.
- Add checkpointing and persistence for model artifacts in `models/`.
- Store historical tick or candle data under `data/` for realistic training.

## Disclaimer

This project is a framework for research and software engineering. It does not guarantee profit or 90% live accuracy. Any real trading system must undergo extensive backtests, forward testing, risk controls, and broker-specific validation.

## License

MIT
