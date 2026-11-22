"""Train department forecasters from CSV data, falling back to generated data."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.predictive.forecaster import DemandForecaster
from scripts.generate_synthetic_data import generate


def load_data(path: Path) -> pd.DataFrame:
    if path.exists():
        frame = pd.read_csv(path, parse_dates=["timestamp"])
    else:
        frame = generate()
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
        print(f"No public file found; generated synthetic-only data at {path}")
    return frame


if __name__ == "__main__":
    data_path = Path("data/synthetic/hourly_admissions.csv")
    dataset = load_data(data_path)
    metrics = DemandForecaster().train(dataset)
    print(pd.DataFrame(metrics).T.to_string(float_format=lambda value: f"{value:.3f}"))