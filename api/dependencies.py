"""Shared model loading and serving helpers."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.config import MODEL_PATH

LOGGER = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Load the serialized end-to-end model pipeline once per process."""
    path = Path(MODEL_PATH)
    if not path.is_file():
        raise FileNotFoundError(f"Modèle non entraîné : {path}")
    LOGGER.info("Chargement du modèle sérialisé")
    return joblib.load(path)


def predict_customer(payload: dict[str, Any]) -> tuple[int, float]:
    """Return class and positive-class probability for one raw customer record."""
    model = get_model()
    row = pd.DataFrame([payload])
    probability = float(model.predict_proba(row)[0, 1])
    return int(probability >= 0.5), probability


def predict_customers(payloads: list[dict[str, Any]]) -> list[tuple[int, float]]:
    """Score a batch in one model call and return class/probability pairs."""
    model = get_model()
    rows = pd.DataFrame(payloads)
    probabilities = model.predict_proba(rows)[:, 1]
    return [(int(probability >= 0.5), float(probability)) for probability in probabilities]
