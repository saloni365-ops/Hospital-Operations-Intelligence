from backend.simulation.engine import DEPARTMENTS, HospitalSimulation


def test_seeded_runs_have_identical_operational_trajectory() -> None:
    first = HospitalSimulation(seed=17, horizon=12)
    second = HospitalSimulation(seed=17, horizon=12)
    for _ in range(12):
        first.step()
        second.step()
    for left, right in zip(first.history, second.history):
        for field in ("arrivals", "occupancy", "queue", "nurses"):
            assert left[field] == right[field]


def test_disruption_is_recorded_and_all_wards_remain_present() -> None:
    simulation = HospitalSimulation(seed=2, horizon=3)
    simulation.inject_event("bed_closure", "Cardiology", duration=2)
    state = simulation.step()
    assert [department["name"] for department in state["departments"]] == list(DEPARTMENTS)
    assert "bed closure triggered" in " ".join(state["event_log"])
    assert state["metrics"]["unmet_demand"] >= 0