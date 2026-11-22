"""Export report-ready figures and tables from measured result CSV files."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MODE_ORDER = ["hybrid", "quantum", "predictive"]
MODE_COLORS = {"hybrid": "#12B5A6", "quantum": "#7C5CFF", "predictive": "#FFB020"}


def export() -> list[Path]:
    results_dir = Path("results")
    csv_path = results_dir / "mode_comparison.csv"
    out_dir = Path("docs/report_figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        raise FileNotFoundError("Run scripts/run_experiments.py first to create results/mode_comparison.csv")

    frame = pd.read_csv(csv_path)
    created: list[Path] = []

    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"]})

    fig, ax = plt.subplots(figsize=(7.2, 4.3), dpi=300)
    for mode in MODE_ORDER:
        rows = frame[frame["mode"] == mode]
        ax.scatter(rows["seed"], rows["unmet_demand_total"], color=MODE_COLORS[mode], s=22, label=mode.capitalize())
    ax.set_xlabel("Seed")
    ax.set_ylabel("Cumulative unmet demand (patient-hours)")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    for suffix in ("png", "svg"):
        path = out_dir / f"fig_5_1_mode_unmet_demand.{suffix}"
        fig.savefig(path, dpi=300 if suffix == "png" else None, bbox_inches="tight", facecolor="white")
        created.append(path)
    plt.close(fig)

    summary = frame.groupby(["mode", "scenario"])[["bed_utilization", "unmet_demand_total", "nurse_balance", "optimizer_ms_mean", "allocation_quality", "recovery_time_hours"]].agg(["mean", "std"]).round(4)
    summary.to_csv(out_dir / "table_5_1_mode_summary.csv")
    (out_dir / "table_5_1_mode_summary.md").write_text(summary.to_markdown(), encoding="utf-8")

    return created


if __name__ == "__main__":
    print("\n".join(str(path) for path in export()))
