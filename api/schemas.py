"""Validated API request and response models."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerData(BaseModel):
    """Pre-campaign customer attributes (call duration deliberately excluded)."""
    model_config = ConfigDict(extra="forbid")
    age: int = Field(ge=18, le=120)
    job: str
    marital: str
    education: str
    default: Literal["yes", "no"]
    balance: float
    housing: Literal["yes", "no"]
    loan: Literal["yes", "no"]
    contact: str
    day: int = Field(ge=1, le=31)
    month: str
    campaign: int = Field(ge=1)
    pdays: int = Field(ge=-1)
    previous: int = Field(ge=0)
    poutcome: str


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_version: str


class BatchPredictionRequest(BaseModel):
    """Batch request with a strict upper bound to protect API resources."""
    customers: list[CustomerData] = Field(min_length=1, max_length=10_000)


class BatchPredictionResponse(BaseModel):
    processed_count: int
    predictions: list[PredictionResponse]
