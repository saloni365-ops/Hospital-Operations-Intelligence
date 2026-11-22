from backend.simulation.failure_detector import detect_failures


def test_detects_measured_demand_failure_from_trace() -> None:
    trace = []
    for step in range(6):
        trace.append({
            "step": step,
            "unmet_demand": 4,
            "occupancy": {"General Medicine": 3},
            "capacity": {"General Medicine": 18},
            "nurses": {"General Medicine": 8},
            "arrivals": {"General Medicine": 5},
            "forecast": {"General Medicine": 1},
        })

    failures = detect_failures("predictive", 42, "admission_surge", trace, [])

    assert any(failure["type"] == "DEMAND_MISS" for failure in failures)
    assert any(failure["type"] == "FORECAST_MISS" for failure in failures)
