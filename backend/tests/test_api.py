from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_simulation_control_and_event_injection() -> None:
    assert client.post("/simulation/start", json={"seed": 31, "horizon": 4}).status_code == 200
    assert client.post("/simulation/mode", json={"mode": "hybrid"}).status_code == 200
    assert client.post("/simulation/events", json={"kind": "surge", "duration": 2}).status_code == 200
    state = client.post("/simulation/step").json()
    assert state["step"] == 1
    assert len(state["departments"]) == 4
    assert client.get("/metrics").json()["steps"] == 1


def test_comparison_returns_measured_mode_results() -> None:
    response = client.get("/comparison?seed=9&horizon=2")
    assert response.status_code == 200
    results = response.json()["results"]
    assert set(results) == {"predictive", "quantum", "hybrid"}
    assert all(result["optimizer_ms"] >= 0 for result in results.values())


def test_websocket_streams_state() -> None:
    with client.websocket_connect("/ws/state") as websocket:
        state = websocket.receive_json()
    assert state["mode"] in {"predictive", "quantum", "hybrid"}
    assert len(state["departments"]) == 4