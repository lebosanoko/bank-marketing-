"""Environment-backed application settings."""
from __future__ import annotations

import os

DATA_PATH = os.getenv("DATA_PATH", "/app/bank/bank-full.csv")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://bank:bank@localhost:5432/bank_marketing")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0")
TARGET = "y"
RANDOM_STATE = 42
