"""Threshold-based measured failure detection shared by every mode."""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any


def load_thresholds() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "config" / "failure_thresholds.yaml"
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def detect_failures(mode: str, seed: int, scenario: str, trace: list[dict[str, Any]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    thresholds = load_thresholds()
    failures: list[dict[str, Any]] = []
    demand_run = 0
    capacity_run = 0
    staffing_run = 0
    forecast_window: dict[str, list[float]] = {}

    for record in trace:
        hour = record["step"]
        unmet = record["unmet_demand"]
        demand_run = demand_run + 1 if unmet >= thresholds["unmet_demand"]["minimum_patients"] else 0
        if demand_run == thresholds["unmet_demand"]["consecutive_hours"]:
            failures.append(_failure(mode, seed, scenario, hour - demand_run + 1, hour, "All wards", "DEMAND_MISS", "high", f"Unmet demand reached {unmet} for {demand_run} consecutive hours", {"unmet_demand": unmet, "consecutive_hours": demand_run}))

        over = [ward for ward, occupied in record["occupancy"].items() if occupied / max(1, record["capacity"].get(ward, 1)) >= thresholds["capacity"]["occupancy_ratio"]]
        capacity_run = capacity_run + 1 if over else 0
        if over and capacity_run == thresholds["capacity"]["consecutive_hours"]:
            failures.append(_failure(mode, seed, scenario, hour - capacity_run + 1, hour, over[0], "OVERCAPACITY", "high", f"{over[0]} occupancy remained at or above {thresholds['capacity']['occupancy_ratio']:.0%}", {"occupancy_ratio": record["occupancy"][over[0]] / max(1, record["capacity"][over[0]])}))

        breaches = [ward for ward, occupancy in record["occupancy"].items() if occupancy / max(1, record["nurses"].get(ward, 1)) > thresholds["staffing"]["patients_per_nurse"]]
        staffing_run = staffing_run + 1 if breaches else 0
        if breaches and staffing_run == thresholds["staffing"]["consecutive_hours"]:
            failures.append(_failure(mode, seed, scenario, hour - staffing_run + 1, hour, breaches[0], "STAFFING_BREACH", "critical", f"{breaches[0]} exceeded the safe patients-per-nurse ratio", {"patients_per_nurse": record["occupancy"][breaches[0]] / max(1, record["nurses"][breaches[0]])}))

        if mode in {"predictive", "hybrid"}:
            misses: list[tuple[str, float]] = []
            for ward in record["arrivals"]:
                actual = record["arrivals"][ward]
                forecast = record["forecast"][ward]
                forecast_window.setdefault(ward, []).append(abs(actual - forecast) / max(1, actual))
                window = forecast_window[ward][-thresholds["forecast"]["window_hours"]:]
                if len(window) >= thresholds["forecast"]["window_hours"]:
                    misses.append((ward, sum(window) / len(window) * 100))
            if misses:
                ward, mape = max(misses, key=lambda item: item[1])
                if mape >= thresholds["forecast"]["mape_percent"]:
                    failures.append(_failure(mode, seed, scenario, hour - thresholds["forecast"]["window_hours"] + 1, hour, ward, "FORECAST_MISS", "medium", f"Forecast MAPE reached {mape:.1f}% for {ward} over the window", {"mape_percent": mape}))

    return failures


def _failure(mode: str, seed: int, scenario: str, t_start: int, t_end: int, department: str, kind: str, severity: str, root_cause: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"mode": mode, "seed": seed, "scenario": scenario, "t_start": t_start, "t_end": t_end, "department": department, "type": kind, "severity": severity, "root_cause": root_cause, "evidence": evidence}
