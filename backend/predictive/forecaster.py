"""Per-department time-series forecasting with a tree baseline and XGBoost."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from backend.simulation.engine import DEPARTMENTS

FEATURES = ["hour", "day_of_week", "lag_1", "lag_24", "rolling_6", "rolling_24", "disruption"]


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build causal calendar, lag, rolling and disruption features."""
    result = frame.copy().sort_values("timestamp")
    result["hour"] = result.timestamp.dt.hour
    result["day_of_week"] = result.timestamp.dt.dayofweek
    group = result.groupby("department", sort=False)["admissions"]
    result["lag_1"] = group.shift(1)
    result["lag_24"] = group.shift(24)
    result["rolling_6"] = group.transform(lambda series: series.shift(1).rolling(6, min_periods=1).mean())
    result["rolling_24"] = group.transform(lambda series: series.shift(1).rolling(24, min_periods=1).mean())
    result["disruption"] = result.get("disruption", 0)
    return result.dropna(subset=["lag_1", "lag_24"])


@dataclass
class DemandForecaster:
    """Fits one model per ward and reports held-out chronological accuracy."""

    model_dir: Path = Path("models")
    use_xgboost: bool = True

    def train(self, frame: pd.DataFrame) -> dict[str, dict[str, float]]:
        features = make_features(frame)
        metrics: dict[str, dict[str, float]] = {}
        self.model_dir.mkdir(parents=True, exist_ok=True)
        for department in DEPARTMENTS:
            rows = features[features.department == department]
            split = max(1, int(len(rows) * 0.8))
            train, test = rows.iloc[:split], rows.iloc[split:]
            baseline = HistGradientBoostingRegressor(max_iter=100, random_state=17).fit(train[FEATURES], train.admissions)
            model = baseline
            if self.use_xgboost:
                try:
                    from xgboost import XGBRegressor
                    model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, objective="reg:squarederror", n_jobs=1, random_state=17)
                    model.fit(train[FEATURES], train.admissions)
                except ImportError:
                    model = baseline
            truth = test.admissions.to_numpy()
            baseline_predictions = np.maximum(0, baseline.predict(test[FEATURES])) if len(test) else np.array([])
            predictions = np.maximum(0, model.predict(test[FEATURES])) if len(test) else np.array([])
            def score(values: np.ndarray) -> dict[str, float]:
                return {"mae": float(mean_absolute_error(truth, values)) if len(test) else 0.0,
                    "rmse": float(math.sqrt(mean_squared_error(truth, values))) if len(test) else 0.0,
                    "mape": float(np.mean(np.abs((truth - values) / np.maximum(truth, 1))) * 100) if len(test) else 0.0}
            metrics[department] = {**score(predictions), **{f"baseline_{key}": value for key, value in score(baseline_predictions).items()}}
            joblib.dump(baseline, self.model_dir / f"{_slug(department)}_baseline.joblib")
            joblib.dump(model, self.model_dir / f"{_slug(department)}.joblib")
        return metrics

    def predict(self, frame: pd.DataFrame, horizon: int = 24) -> dict[str, list[float]]:
        """Recursively predict hourly arrivals for each department."""
        if horizon < 1:
            raise ValueError("horizon must be positive")
        result: dict[str, list[float]] = {}
        for dept in DEPARTMENTS:
            model_path = self.model_dir / f"{_slug(dept)}.joblib"
            model = joblib.load(model_path)
            history = frame[frame.department == dept].sort_values("timestamp").admissions.astype(float).tolist()
            forecast: list[float] = []
            last_time = pd.Timestamp(frame.timestamp.max())
            for offset in range(1, horizon + 1):
                current = last_time + pd.Timedelta(hours=offset)
                values = np.array(history, dtype=float)
                row = pd.DataFrame([[current.hour, current.dayofweek, values[-1], values[-24] if len(values) >= 24 else values.mean(), values[-6:].mean(), values[-24:].mean(), 0]], columns=FEATURES)
                value = max(0.0, float(model.predict(row)[0]))
                forecast.append(value)
                history.append(value)
            result[dept] = forecast
        return result


def _slug(value: str) -> str:
    return value.lower().replace(" ", "_")
