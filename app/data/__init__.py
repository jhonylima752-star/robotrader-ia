from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.models_dir = self.project_root / "models"
        self.logs_dir = self.project_root / "logs"

        self.symbols = os.getenv(
            "SYMBOLS",
            "EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,NZDUSD",
        ).split(",")
        self.forecast_horizon_seconds = int(os.getenv("FORECAST_HORIZON_SECONDS", "120"))

        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        self.mt5_login = int(os.getenv("MT5_LOGIN", "0") or 0)
        self.mt5_password = os.getenv("MT5_PASSWORD", "")
        self.mt5_server = os.getenv("MT5_SERVER", "")

        self.max_lookback_bars = int(os.getenv("MAX_LOOKBACK_BARS", "5000"))
        self.signal_confidence_threshold = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.55"))


settings = Settings()
