"""In-memory run trace and comparison job store with replay-safe step records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class TraceStore:
    runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    jobs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def record_run(self, mode: str, seed: int, scenario: str, history: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
        run_id = str(uuid4())
        self.runs[run_id] = {"id": run_id, "mode": mode, "seed": seed, "scenario": scenario, "trace": history, "events": events}
        return run_id

    def create_job(self, seed: int, horizon: int, scenario: str) -> str:
        job_id = str(uuid4())
        self.jobs[job_id] = {"id": job_id, "status": "running", "progress": 0, "seed": seed, "horizon": horizon, "scenario": scenario, "results": None}
        return job_id


trace_store = TraceStore()
