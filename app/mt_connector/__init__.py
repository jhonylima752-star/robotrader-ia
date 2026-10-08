from pathlib import Path
import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.data.loader import build_features


class SignalModel:
    def __init__(self, model=None, feature_columns=None):
        self.model = model or RandomForestClassifier(
            n_estimators=250,
            max_depth=7,
            random_state=42,
            class_weight="balanced",
        )
        self.feature_columns = feature_columns or []

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.feature_columns = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame):
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)

    def save(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        artifact = {
            "feature_columns": self.feature_columns,
            "model": self.model,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"feature_columns": self.feature_columns}, fh)

        # sklearn models are picklable by pathlib; store as a native pickle artifact.
        import pickle

        with open(str(path) + ".pkl", "wb") as handle:
            pickle.dump(self.model, handle)

    @classmethod
    def load(cls, path: str | Path):
        import pickle

        path = Path(path)
        with open(str(path) + ".pkl", "rb") as handle:
            model = pickle.load(handle)
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return cls(model=model, feature_columns=payload.get("feature_columns", []))


def build_target(series: pd.Series, horizon: int = 5, threshold: float = 0.0008) -> pd.Series:
    future = series.shift(-horizon)
    direction = (future - series) / series
    return (direction > threshold).astype(int)


def prepare_dataset(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.0008) -> tuple[pd.DataFrame, pd.Series]:
    frame = build_features(df).dropna().copy()
    frame["target"] = build_target(frame["close"], horizon=horizon, threshold=threshold)
    feature_columns = [
        "ret_1m",
        "ret_5m",
        "ret_15m",
        "sma_fast",
        "sma_slow",
        "spread",
        "volatility",
        "rsi",
        "momentum",
        "atr",
        "feature_score",
    ]
    X = frame[feature_columns]
    y = frame["target"]
    return X, y


def train_model_for_symbol(df: pd.DataFrame, symbol: str = "EURUSD", horizon: int = 5) -> dict:
    X, y = prepare_dataset(df, horizon=horizon)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False, random_state=42)

    model = SignalModel()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)

    metrics = {
        "symbol": symbol,
        "accuracy": float(accuracy),
        "sample_count": int(len(X)),
        "classification_report": classification_report(y_test, preds, zero_division=0),
    }
    return metrics


def train_model_for_all_pairs(df_map: dict[str, pd.DataFrame]) -> dict:
    results = {}
    for symbol, frame in df_map.items():
        results[symbol] = train_model_for_symbol(frame, symbol=symbol)
    return results
