from fastapi.testclient import TestClient

from api.main import app
from api import main

client = TestClient(app)


def test_health_when_model_ready(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_model", lambda: object())
    assert client.get("/health").json() == {"status": "healthy"}


def test_model_info_when_model_ready(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_model", lambda: object())
    response = client.get("/model-info")
    assert response.status_code == 200
    assert response.json()["required_features"]
    assert response.json()["max_batch_size"] == 10_000
    assert "model_version" in response.json()


def test_predict_valid_and_invalid_payload(monkeypatch) -> None:
    monkeypatch.setattr(main, "predict_customer", lambda payload: (1, 0.78))
    payload = {
        "age": 42, "job": "technician", "marital": "married", "education": "secondary",
        "default": "no", "balance": 1200, "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["prediction"] == 1
    assert client.post("/predict", json={"age": 42}).status_code == 422


def test_batch_prediction(monkeypatch) -> None:
    monkeypatch.setattr(main, "predict_customers", lambda payloads: [(1, 0.78), (0, 0.22)])
    customer = {
        "age": 42, "job": "technician", "marital": "married", "education": "secondary",
        "default": "no", "balance": 1200, "housing": "yes", "loan": "no", "contact": "cellular",
        "day": 15, "month": "may", "campaign": 2, "pdays": -1, "previous": 0, "poutcome": "unknown",
    }
    response = client.post("/predict/batch", json={"customers": [customer, customer]})
    assert response.status_code == 200
    assert response.json()["processed_count"] == 2
    assert [row["prediction"] for row in response.json()["predictions"]] == [1, 0]
    assert client.post("/predict/batch", json={"customers": []}).status_code == 422
