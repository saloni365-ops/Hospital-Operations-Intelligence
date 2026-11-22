from backend.predictive.forecaster import DemandForecaster
from scripts.generate_synthetic_data import generate


def test_forecaster_trains_baseline_and_predicts_horizon(tmp_path) -> None:
    frame = generate(days=8, seed=3)
    forecaster = DemandForecaster(model_dir=tmp_path, use_xgboost=False)
    metrics = forecaster.train(frame)
    predictions = forecaster.predict(frame, horizon=3)

    assert len(metrics) == 4
    assert all("baseline_mae" in result and result["mae"] >= 0 for result in metrics.values())
    assert all(len(values) == 3 and all(value >= 0 for value in values) for values in predictions.values())