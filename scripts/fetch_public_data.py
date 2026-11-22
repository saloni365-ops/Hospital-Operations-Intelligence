"""Try an optional aggregate public-data CSV URL, then fall back to synthetic data.

Set PUBLIC_HEALTH_DATA_URL to a reachable CSV with timestamp, department, admissions.
No public source is bundled or required; synthetic data is always the fallback.
"""

from pathlib import Path
import os
import sys
from urllib.request import urlopen

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.generate_synthetic_data import generate


def fetch(output: Path) -> str:
    url = os.getenv("PUBLIC_HEALTH_DATA_URL")
    if url:
        try:
            with urlopen(url, timeout=8) as response:
                frame = pd.read_csv(response)
            required = {"timestamp", "department", "admissions"}
            if required.issubset(frame.columns):
                output.parent.mkdir(parents=True, exist_ok=True)
                frame.to_csv(output, index=False)
                return "public CSV"
        except Exception as error:
            print(f"Public data unavailable ({error}); using synthetic fallback")
    output.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(output, index=False)
    return "synthetic fallback"


if __name__ == "__main__":
    destination = Path("data/synthetic/hourly_admissions.csv")
    print(f"Saved {fetch(destination)} dataset to {destination}")