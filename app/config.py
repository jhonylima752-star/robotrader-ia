from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


class Settings:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.models_dir = self.project_root / "models"
        self.logs_dir = self.project_root / "logs"

        self.symbols = [
            s.strip() 
            for s in os.getenv(
                "SYMBOLS",
                "EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,NZDUSD",
            ).split(",") 
            if s.strip()
        ]
        self.forecast_horizon_seconds = _get_env_int("FORECAST_HORIZON_SECONDS", 120)
        self.signal_confidence_threshold = _get_env_float("SIGNAL_CONFIDENCE_THRESHOLD", 0.55)

        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        self.mt5_login = _get_env_int("MT5_LOGIN", 0)
        self.mt5_password = os.getenv("MT5_PASSWORD", "")
        self.mt5_server = os.getenv("MT5_SERVER", "")
        self.mt5_path = os.getenv("MT5_PATH", "")

        self.default_volume = _get_env_float("DEFAULT_VOLUME", 0.01)
        self.max_lookback_bars = _get_env_int("MAX_LOOKBACK_BARS", 5000)
        self.use_simulator = os.getenv("USE_SIMULATOR", "true").lower() == "true"


settings = Settings()
