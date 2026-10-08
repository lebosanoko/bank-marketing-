"""Small local inference helper for a serialized pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


def predict(data: pd.DataFrame, model_path: str | Path = "models/model.pkl") -> list[dict[str, float | int]]:
    """Load an exported pipeline and predict classes with positive-class probabilities."""
    pipeline: Any = joblib.load(model_path)
    probabilities = pipeline.predict_proba(data)[:, 1]
    return [{"prediction": int(probability >= 0.5), "probability": float(probability)} for probability in probabilities]
