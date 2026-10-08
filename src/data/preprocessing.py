"""Preprocessing pipeline for the UCI Bank Marketing data."""
from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAW_NUMERIC_FEATURES = ["age", "balance", "day", "campaign", "pdays", "previous"]
NUMERIC_FEATURES = RAW_NUMERIC_FEATURES + ["age_band", "previously_contacted", "previous_contact_known"]
CATEGORICAL_FEATURES = [
    "job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"
]
FEATURES = RAW_NUMERIC_FEATURES + CATEGORICAL_FEATURES


def prepare_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate features and binary target, excluding post-call duration to prevent leakage."""
    missing = set(FEATURES + ["y"]) - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans le dataset : {sorted(missing)}")
    x = frame[FEATURES].copy()
    y = frame["y"].map({"yes": 1, "no": 0}).astype("int8")
    return x, y


def build_preprocessor() -> ColumnTransformer:
    """Build a leakage-safe transformer that imputes and encodes raw client features."""
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])
