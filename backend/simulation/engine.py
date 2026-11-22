"""Seeded hourly hospital simulation with queues and injectable disruptions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import math
import random
import time
from pathlib import Path

DEPARTMENTS = ("General Medicine", "Cardiology", "Orthopedics", "Neurology")
BASE_BEDS = (18, 12, 14, 10)
BASE_NURSES = (8, 6, 6, 5)
MODES = ("predictive", "quantum", "hybrid")


@dataclass
class Patient:
    department: str
    remaining_hours: int


@dataclass
class Disruption:
    kind: str
    department: str | None = None
    start_step: int = 0
    duration: int = 8
    magnitude: float = 0.3
    applied: bool = False


@dataclass
class HospitalSimulation:
    seed: int = 42
    horizon: int = 168
    mode: str = "hybrid"
    step_index: int = 0
    running: bool = False
    rng: random.Random = field(init=False, repr=False)
    beds: dict[str, list[str]] = field(init=False)
    nurses: dict[str, int] = field(init=False)
    base_nurses: dict[str, int] = field(init=False)
    patients: list[Patient] = field(default_factory=list)
    queues: dict[str, int] = field(init=False)
    events: list[Disruption] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    event_log: list[str] = field(default_factory=list)
    last_allocation: dict[str, int] = field(default_factory=dict)
    last_optimizer_ms: float = 0.0
    _arrivals: dict[str, list[int]] = field(default_factory=dict)
    _closed_beds: dict[str, int] = field(default_factory=dict)
    _forecast_models: dict[str, Any] = field(default_factory=dict, repr=False)
    _event_baselines: dict[int, int] = field(default_factory=dict)
    _recovery_times: dict[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        self.rng = random.Random(self.seed)
        self.beds = {name: ["available"] * cap for name, cap in zip(DEPARTMENTS, BASE_BEDS)}
        self.nurses = dict(zip(DEPARTMENTS, BASE_NURSES))
        self.base_nurses = self.nurses.copy()
        self.queues = dict.fromkeys(DEPARTMENTS, 0)
        self.last_allocation = self.nurses.copy()
        self._arrivals = {d: [] for d in DEPARTMENTS}
        try:
            import joblib
            model_dir = Path(__file__).resolve().parents[2] / "models"
            for dept in DEPARTMENTS:
                path = model_dir / f"{dept.lower().replace(' ', '_')}.joblib"
                if path.exists():
                    self._forecast_models[dept] = joblib.load(path)
        except Exception:
            self._forecast_models.clear()

    def inject_event(self, kind: str, department: str | None = None, duration: int = 8, magnitude: float = 0.3) -> None:
        allowed = {"surge", "nurse_unavailable", "bed_closure", "ed_overload"}
        if kind not in allowed:
            raise ValueError(f"kind must be one of {sorted(allowed)}")
        if department is not None and department not in DEPARTMENTS:
            raise ValueError("unknown department")
        self.events.append(Disruption(kind, department, self.step_index, max(1, duration), magnitude))
        self.event_log.append(f"Scheduled {kind.replace('_', ' ')}" + (f" in {department}" if department else ""))

    def _active(self, event: Disruption) -> bool:
        return event.start_step <= self.step_index < event.start_step + event.duration

    def _forecast(self, dept: str) -> float:
        hour = self.step_index % 24
        weekday = (self.step_index // 24) % 7
        base = {"General Medicine": 2.4, "Cardiology": 1.2, "Orthopedics": 1.25, "Neurology": 0.9}[dept]
        seasonal = 1 + 0.22 * math.sin((hour - 7) * math.pi / 12) + (0.12 if weekday >= 5 else 0)
        surge = 1 + sum(e.magnitude for e in self.events if self._active(e) and e.kind in {"surge", "ed_overload"} and e.department in {None, dept})
        recent_values = self._arrivals[dept][-6:]
        recent = sum(recent_values) / max(1, len(recent_values)) if recent_values else base
        model = self._forecast_models.get(dept)
        if model is not None:
            values = self._arrivals[dept]
            row = [[hour, weekday, values[-1] if values else base, values[-24] if len(values) >= 24 else recent, recent, sum(values[-24:]) / max(1, len(values[-24:])) if values else base, int(surge > 1)]]
            return max(0.0, float(model.predict(row)[0]))
        return max(0.0, 0.65 * base * seasonal * surge + 0.35 * recent)

    def _plan(self, forecasts: dict[str, float]) -> None:
        started = time.perf_counter()
        previous = self.nurses.copy()
        if self.mode == "predictive":
            allocations = {d: 1 for d in DEPARTMENTS}
            unavailable = sum(max(1, round(self.base_nurses[e.department or max(self.base_nurses, key=self.base_nurses.get)] * 0.25)) for e in self.events if self._active(e) and e.kind == "nurse_unavailable")
            budget = max(len(DEPARTMENTS), sum(self.base_nurses.values()) - unavailable)
            target = {d: max(1, round(self.base_nurses[d] * forecasts[d] / 2.4)) for d in DEPARTMENTS}
            priorities = sorted(DEPARTMENTS, key=lambda d: forecasts[d] / max(1, self.base_nurses[d]), reverse=True)
            for dept in priorities:
                allocations[dept] += min(max(0, target[dept] - 1), budget - sum(allocations.values()))
        else:
            from backend.optimization.classical_solver import ClassicalSolver
            from backend.optimization.common import AllocationProblem
            from backend.optimization.dwave_solver import DWaveSolver

            available = {d: max(1, self.base_nurses[d] - (max(1, round(self.base_nurses[d] * 0.25)) if any(self._active(e) and e.kind == "nurse_unavailable" and e.department in {None, d} for e in self.events) else 0)) for d in DEPARTMENTS}
            pool_size = sum(available.values())
            problem = AllocationProblem(list(DEPARTMENTS), {d: forecasts[d] + self.queues[d] for d in DEPARTMENTS}, {d: len(self.beds[d]) - self._closed_beds.get(d, 0) for d in DEPARTMENTS}, pool_size, {d: min(pool_size, self.base_nurses[d] + 4) for d in DEPARTMENTS})
            result = DWaveSolver().solve(problem) if self.mode == "quantum" else ClassicalSolver().solve(problem)
            allocations = result.allocation
            self.last_optimizer_ms = result.runtime_ms
            self.event_log.append(f"{self.mode.title()} allocation: " + ", ".join(f"{d} {n}" for d, n in allocations.items()))
        for event in self.events:
            if self._active(event) and event.kind == "nurse_unavailable":
                target_dept = event.department or max(allocations, key=allocations.get)
                allocations[target_dept] = min(allocations[target_dept], max(1, self.base_nurses[target_dept] - max(1, round(self.base_nurses[target_dept] * 0.25))))
        self.nurses = allocations
        self.last_allocation = allocations.copy()
        donors = [[d, previous[d] - allocations[d]] for d in DEPARTMENTS if previous[d] > allocations[d]]
        receivers = [[d, allocations[d] - previous[d]] for d in DEPARTMENTS if allocations[d] > previous[d]]
        donor_index = receiver_index = 0
        while donor_index < len(donors) and receiver_index < len(receivers):
            moved = min(donors[donor_index][1], receivers[receiver_index][1])
            if moved:
                self.event_log.append(f"Moved {moved} nurse{'s' if moved != 1 else ''} from {donors[donor_index][0]} to {receivers[receiver_index][0]} based on forecast demand")
                donors[donor_index][1] -= moved
                receivers[receiver_index][1] -= moved
            if not donors[donor_index][1]: donor_index += 1
            if not receivers[receiver_index][1]: receiver_index += 1
        if self.mode == "predictive":
            self.last_optimizer_ms = (time.perf_counter() - started) * 1000

    def step(self) -> dict[str, Any]:
        if self.step_index >= self.horizon:
            self.running = False
            return self.state()
        remaining: list[Patient] = []
        for patient in self.patients:
            patient.remaining_hours -= 1
            if patient.remaining_hours > 0:
                remaining.append(patient)
            else:
                idx = next((i for i, status in enumerate(self.beds[patient.department]) if status == "occupied"), None)
                if idx is not None:
                    self.beds[patient.department][idx] = "available"
        self.patients = remaining
        self._closed_beds = {e.department: max(1, round(len(self.beds[e.department]) * 0.2)) for e in self.events if self._active(e) and e.kind == "bed_closure" and e.department}
        forecasts = {d: self._forecast(d) for d in DEPARTMENTS}
        self._plan(forecasts)
        arrivals: dict[str, int] = {}
        for dept in DEPARTMENTS:
            hour = self.step_index % 24
            weekday = (self.step_index // 24) % 7
            mean = {"General Medicine": 2.4, "Cardiology": 1.2, "Orthopedics": 1.25, "Neurology": 0.9}[dept]
            mean *= max(0.35, 1 + 0.22 * math.sin((hour - 7) * math.pi / 12) + (0.12 if weekday >= 5 else 0))
            mean *= 1 + sum(e.magnitude for e in self.events if self._active(e) and e.kind in {"surge", "ed_overload"} and e.department in {None, dept})
            count = max(0, int(self.rng.gauss(mean, math.sqrt(mean))))
            arrivals[dept] = count
            self._arrivals[dept].append(count)
            for _ in range(count):
                occupied = sum(status == "occupied" for status in self.beds[dept])
                staffed_limit = min(len(self.beds[dept]) - self._closed_beds.get(dept, 0), self.nurses[dept] * 4)
                open_bed = next((i for i, status in enumerate(self.beds[dept]) if status == "available" and i >= self._closed_beds.get(dept, 0)), None) if occupied < staffed_limit else None
                if open_bed is None:
                    self.queues[dept] += 1
                else:
                    self.beds[dept][open_bed] = "occupied"
                    self.patients.append(Patient(dept, max(2, round(self.rng.lognormvariate(2.2, 0.45)))))
            while self.queues[dept] and sum(s == "occupied" for s in self.beds[dept]) < min(len(self.beds[dept]) - self._closed_beds.get(dept, 0), self.nurses[dept] * 4) and any(s == "available" for s in self.beds[dept][self._closed_beds.get(dept, 0):]):
                idx = next(i for i, s in enumerate(self.beds[dept]) if i >= self._closed_beds.get(dept, 0) and s == "available")
                self.beds[dept][idx] = "occupied"
                self.patients.append(Patient(dept, max(2, round(self.rng.lognormvariate(2.2, 0.45)))))
                self.queues[dept] -= 1
        for event in self.events:
            if not event.applied and self._active(event):
                event.applied = True
                self._event_baselines[id(event)] = sum(self.queues.values())
                self.event_log.append(f"Step {self.step_index}: {event.kind.replace('_', ' ')} triggered; {self.mode} plan updated")
        occupancy = {d: sum(s == "occupied" for s in self.beds[d]) for d in DEPARTMENTS}
        balance = _std([occupancy[d] / max(1, self.nurses[d]) for d in DEPARTMENTS])
        for event in self.events:
            key = id(event)
            if event.applied and key not in self._recovery_times and self.step_index >= event.start_step + event.duration and sum(self.queues.values()) <= self._event_baselines.get(key, 0):
                self._recovery_times[key] = self.step_index - event.start_step
        forecast_errors = [abs(arrivals[d] - forecasts[d]) for d in DEPARTMENTS]
        forecast_mae = sum(forecast_errors) / len(DEPARTMENTS)
        forecast_rmse = math.sqrt(sum(error * error for error in forecast_errors) / len(DEPARTMENTS))
        forecast_mape = sum(forecast_errors[i] / max(1, arrivals[d]) for i, d in enumerate(DEPARTMENTS)) / len(DEPARTMENTS) * 100
        demand_total = max(0.1, sum(forecasts.values()))
        nurse_total = max(1, sum(self.nurses.values()))
        share_error = sum(abs(self.nurses[d] / nurse_total - forecasts[d] / demand_total) for d in DEPARTMENTS)
        allocation_quality = max(0.0, 1 - share_error / 2)
        record: dict[str, Any] = {
            "step": self.step_index, "hour": self.step_index % 24, "arrivals": arrivals,
            "forecast": forecasts, "occupancy": occupancy,
            "capacity": {d: len(self.beds[d]) - self._closed_beds.get(d, 0) for d in DEPARTMENTS},
            "nurses": self.nurses.copy(), "queue": self.queues.copy(),
            "utilization": sum(occupancy.values()) / sum(max(1, len(self.beds[d]) - self._closed_beds.get(d, 0)) for d in DEPARTMENTS),
            "unmet_demand": sum(self.queues.values()), "nurse_balance": balance,
            "optimizer_ms": self.last_optimizer_ms, "forecast_mae": forecast_mae,
            "forecast_rmse": forecast_rmse, "forecast_mape": forecast_mape,
            "allocation_quality": allocation_quality,
            "recovery_time_hours": max(self._recovery_times.values(), default=-1),
        }
        self.history.append(record)
        self.step_index += 1
        if self.step_index >= self.horizon:
            self.running = False
        return self.state()

    def state(self) -> dict[str, Any]:
        last = self.history[-1] if self.history else {}
        return {
            "seed": self.seed, "step": self.step_index, "horizon": self.horizon,
            "running": self.running, "mode": self.mode,
            "departments": [{"name": d, "beds": ["unavailable" if i < self._closed_beds.get(d, 0) and status == "available" else status for i, status in enumerate(self.beds[d])], "capacity": len(self.beds[d]) - self._closed_beds.get(d, 0),
                "occupied": sum(s == "occupied" for s in self.beds[d]), "queue": self.queues[d],
                "nurses": self.nurses[d], "forecast": last.get("forecast", {}).get(d, 0),
                "arrivals": last.get("arrivals", {}).get(d, 0)} for d in DEPARTMENTS],
            "metrics": last, "history": self.history[-168:], "events": [asdict(e) for e in self.events],
            "event_log": self.event_log[-30:], "optimizer_ms": self.last_optimizer_ms,
        }


def _std(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))