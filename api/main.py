"""FastAPI prediction service."""
from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, status

from api.dependencies import get_model, predict_customer, predict_customers
from api.schemas import BatchPredictionRequest, BatchPredictionResponse, CustomerData, PredictionResponse
from src.config import MODEL_PATH, MODEL_VERSION
from src.data.preprocessing import FEATURES

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
app = FastAPI(title="Customer Subscription Prediction API", version=MODEL_VERSION)


@app.get("/health")
def health() -> dict[str, str]:
    """Report process and model readiness."""
    try:
        get_model()
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Model not trained yet") from None
    except Exception:
        LOGGER.exception("Model loading failed")
        raise HTTPException(status_code=503, detail="Model unavailable") from None
    return {"status": "healthy"}


@app.get("/model-info")
def model_info() -> dict[str, object]:
    """Return serving model metadata without exposing local file contents."""
    try:
        get_model()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet") from None
    return {
        "model_version": MODEL_VERSION,
        "artifact": MODEL_PATH.rsplit("/", 1)[-1],
        "required_features": FEATURES,
        "max_batch_size": 10_000,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(data: CustomerData) -> PredictionResponse:
    """Predict subscription probability from pre-call customer features."""
    try:
        prediction, probability = predict_customer(data.model_dump())
        LOGGER.info("Prediction served (positive=%s)", prediction)
        return PredictionResponse(prediction=prediction, probability=probability, model_version=MODEL_VERSION)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet") from None
    except Exception:
        LOGGER.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from None


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(data: BatchPredictionRequest) -> BatchPredictionResponse:
    """Score up to 10,000 raw customer rows in one request without logging their data."""
    try:
        payloads = [customer.model_dump() for customer in data.customers]
        scored = predict_customers(payloads)
        LOGGER.info("Batch prediction served (%s rows)", len(scored))
        return BatchPredictionResponse(
            processed_count=len(scored),
            predictions=[
                PredictionResponse(prediction=prediction, probability=probability, model_version=MODEL_VERSION)
                for prediction, probability in scored
            ],
        )
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet") from None
    except Exception:
        LOGGER.exception("Batch prediction failed")
        raise HTTPException(status_code=500, detail="Batch prediction failed") from None
