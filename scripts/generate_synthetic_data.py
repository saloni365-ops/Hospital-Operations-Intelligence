"""Generate deterministic hourly synthetic hospital admissions."""

from pathlib import Path
import argparse
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.simulation.engine import DEPARTMENTS


def generate(days: int = 180, seed: int = 42) -> pd.DataFrame:
    """Return hourly department admissions with seasonality and surge periods."""
    import numpy as np
    rng = np.random.default_rng(seed)
    rows = []
    times = pd.date_range("2025-01-06", periods=days * 24, freq="h")
    bases = [2.4, 1.2, 1.25, 0.9]
    for dept, base in zip(DEPARTMENTS, bases):
        for index, timestamp in enumerate(times):
            surge = 0.45 if 900 <= index < 960 or 2400 <= index < 2460 else 0
            mean = base * (1 + 0.2 * np.sin((timestamp.hour - 7) * np.pi / 12) + (0.1 if timestamp.dayofweek >= 5 else 0) + surge)
            rows.append({"timestamp": timestamp, "department": dept, "admissions": int(rng.poisson(max(0.1, mean))), "disruption": int(surge > 0)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/hourly_admissions.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataset = generate(args.days, args.seed)
    dataset.to_csv(args.output, index=False)
    print(f"Wrote {len(dataset)} records to {args.output}")