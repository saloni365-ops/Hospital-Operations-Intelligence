"""Simulation control and live-state API."""

from __future__ import annotations

import asyncio
import math
import threading
from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from backend.simulation.engine import DEPARTMENTS, HospitalSimulation
from backend.simulation.failure_detector import detect_failures
from backend.simulation.trace_store import trace_store

router = APIRouter()
simulation = HospitalSimulation()


class StartRequest(BaseModel):
    seed: int = 42
    horizon: int = Field(default=168, ge=1, le=720)


class SettingsRequest(BaseModel):
    seed: int | None = Field(default=None, ge=0)
    horizon: int | None = Field(default=None, ge=1, le=720)


class ModeRequest(BaseModel):
    mode: Literal["predictive", "quantum", "hybrid"]


class EventRequest(BaseModel):
    kind: Literal["surge", "nurse_unavailable", "bed_closure", "ed_overload"]
    department: str | None = None
    duration: int = Field(default=8, ge=1, le=168)
    magnitude: float = Field(default=0.3, ge=0, le=2)


@router.post("/simulation/start")
def start(request: StartRequest) -> dict:
    global simulation
    simulation = HospitalSimulation(seed=request.seed, horizon=request.horizon, mode=simulation.mode)
    simulation.running = True
    return simulation.state()


@router.post("/simulation/pause")
def pause() -> dict:
    simulation.running = False
    return simulation.state()


@router.post("/simulation/settings")
def update_settings(request: SettingsRequest) -> dict:
    if request.seed is not None:
        simulation.seed = request.seed
        simulation.rng.seed(request.seed)
    if request.horizon is not None:
        simulation.horizon = request.horizon
        simulation.running = simulation.running and simulation.step_index < request.horizon
    return simulation.state()


@router.post("/simulation/reset")
def reset(request: StartRequest | None = None) -> dict:
    global simulation
    simulation = HospitalSimulation(seed=request.seed if request else 42, horizon=request.horizon if request else 168, mode=simulation.mode)
    return simulation.state()


@router.post("/simulation/step")
def step() -> dict:
    return simulation.step()


@router.post("/simulation/mode")
def set_mode(request: ModeRequest) -> dict:
    simulation.mode = request.mode
    name = {"hybrid": "Dynamic Hybrid Intelligence", "quantum": "Quantum Optimization", "predictive": "Predictive AI"}[request.mode]
    simulation.event_log.append(f"Switched to {name}; allocation policy updated")
    return simulation.state()


@router.post("/simulation/events")
def inject_event(request: EventRequest) -> dict:
    try:
        simulation.inject_event(request.kind, request.department, request.duration, request.magnitude)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    return simulation.state()


@router.get("/simulation/state")
def state() -> dict:
    return simulation.state()


@router.get("/metrics")
def metrics() -> dict:
    history = simulation.history
    actual = [r["arrivals"][d] for r in history for d in DEPARTMENTS]
    forecast = [r["forecast"][d] for r in history for d in DEPARTMENTS]
    mae = sum(abs(a - f) for a, f in zip(actual, forecast)) / max(1, len(actual))
    rmse = math.sqrt(sum((a - f) ** 2 for a, f in zip(actual, forecast)) / max(1, len(actual)))
    mape = sum(abs(a - f) / max(1, a) for a, f in zip(actual, forecast)) / max(1, len(actual)) * 100
    last = history[-1] if history else {}
    return {"mae": mae, "rmse": rmse, "mape": mape, "bed_utilization": last.get("utilization", 0), "unmet_demand": last.get("unmet_demand", 0), "nurse_balance": last.get("nurse_balance", 0), "allocation_quality": last.get("allocation_quality", 0), "recovery_time_hours": last.get("recovery_time_hours", -1), "optimizer_ms": simulation.last_optimizer_ms, "steps": len(history)}


@router.get("/comparison")
def comparison(seed: int = 42, horizon: int = Query(default=48, ge=1, le=168)) -> dict:
    results = {}
    scenario = [("surge", 24, 12)]
    for mode in ("predictive", "quantum", "hybrid"):
        run = HospitalSimulation(seed=seed, horizon=horizon, mode=mode)
        for kind, at, duration in scenario:
            if at < horizon:
                run.events.append(__import__("backend.simulation.engine", fromlist=["Disruption"]).Disruption(kind, None, at, duration, 0.3))
        for _ in range(horizon):
            run.step()
        hist = run.history
        results[mode] = {
            "bed_utilization": sum(r["utilization"] for r in hist) / max(1, len(hist)),
            "unmet_demand": sum(r["unmet_demand"] for r in hist),
            "nurse_balance": sum(r["nurse_balance"] for r in hist) / max(1, len(hist)),
            "optimizer_ms": sum(r["optimizer_ms"] for r in hist) / max(1, len(hist)),
            "final_queue": hist[-1]["unmet_demand"] if hist else 0,
        }
    return {"seed": seed, "horizon": horizon, "scenario": "30% admissions surge at hour 24", "results": results}


@router.websocket("/ws/state")
async def websocket_state(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            if simulation.running:
                simulation.step()
            await websocket.send_json(simulation.state())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return


@router.get("/failures")
def failures(scenario: str = "admission_surge", seeds: str = "11,23,42", horizon: int = 72) -> dict:
    failures: list[dict] = []
    run_ids: dict[str, str] = {}
    horizon = max(1, min(horizon, 720))
    for seed_text in seeds.split(","):
        seed = int(seed_text.strip())
        for mode in ("hybrid", "quantum", "predictive"):
            run = HospitalSimulation(seed=seed, horizon=horizon, mode=mode)
            kind = "surge" if scenario == "admission_surge" else "nurse_unavailable" if scenario == "nurse_shortage" else "bed_closure" if scenario == "bed_closure" else "ed_overload"
            department = "General Medicine" if scenario == "nurse_shortage" else "Cardiology" if scenario == "bed_closure" else None
            run.events.append(__import__("backend.simulation.engine", fromlist=["Disruption"]).Disruption(kind, department, 24, 12, 0.3 if kind != "ed_overload" else 0.5))
            for _ in range(horizon):
                run.step()
            run_id = trace_store.record_run(mode, seed, scenario, run.history, [asdict(event) for event in run.events])
            run_ids[f"{mode}:{seed}"] = run_id
            failures.extend(detect_failures(mode, seed, scenario, run.history, [asdict(event) for event in run.events]))
    return {"failures": failures, "thresholds": __import__("backend.simulation.failure_detector", fromlist=["load_thresholds"]).load_thresholds(), "runs": run_ids}


@router.get("/runs/{run_id}/trace")
def run_trace(run_id: str) -> dict:
    if run_id not in trace_store.runs:
        raise HTTPException(404, "Run trace not found")
    return trace_store.runs[run_id]


@router.post("/comparison/run")
def start_comparison(seed: int = 42, horizon: int = Query(default=48, ge=1, le=168), scenario: str = "admission_surge") -> dict:
    job_id = trace_store.create_job(seed, horizon, scenario)

    def execute() -> None:
        results = {}
        modes = ("hybrid", "quantum", "predictive")
        for index, mode in enumerate(modes, start=1):
            run = HospitalSimulation(seed=seed, horizon=horizon, mode=mode)
            kind = "surge" if scenario == "admission_surge" else "nurse_unavailable" if scenario == "nurse_shortage" else "bed_closure" if scenario == "bed_closure" else "ed_overload"
            department = "General Medicine" if scenario == "nurse_shortage" else "Cardiology" if scenario == "bed_closure" else None
            magnitude = 0.5 if kind == "ed_overload" else 0.3
            run.events.append(__import__("backend.simulation.engine", fromlist=["Disruption"]).Disruption(kind, department, 24 if horizon > 24 else 1, 12, magnitude))
            for _ in range(horizon):
                run.step()
            trace_store.record_run(mode, seed, scenario, run.history, [asdict(event) for event in run.events])
            results[mode] = {"bed_utilization": sum(r["utilization"] for r in run.history) / max(1, len(run.history)), "unmet_demand": sum(r["unmet_demand"] for r in run.history), "nurse_balance": sum(r["nurse_balance"] for r in run.history) / max(1, len(run.history)), "optimizer_ms": sum(r["optimizer_ms"] for r in run.history) / max(1, len(run.history)), "final_queue": run.history[-1]["unmet_demand"] if run.history else 0}
            trace_store.jobs[job_id]["progress"] = round(index / len(modes) * 100)
        trace_store.jobs[job_id]["results"] = results
        trace_store.jobs[job_id]["status"] = "complete"

    threading.Thread(target=execute, daemon=True).start()
    return trace_store.jobs[job_id]


@router.get("/comparison/{job_id}")
def comparison_job(job_id: str) -> dict:
    if job_id not in trace_store.jobs:
        raise HTTPException(404, "Comparison job not found")
    return trace_store.jobs[job_id]