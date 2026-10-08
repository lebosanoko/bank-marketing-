import pandas as pd

from src.data.preprocessing import build_preprocessor, prepare_frame
from src.features.engineering import engineer_features


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame({
        "age": [42, 35], "job": ["technician", "admin."], "marital": ["married", "single"],
        "education": ["secondary", "tertiary"], "default": ["no", "no"], "balance": [1200, 0],
        "housing": ["yes", "no"], "loan": ["no", "no"], "contact": ["cellular", "unknown"],
        "day": [15, 5], "month": ["may", "jun"], "campaign": [2, 1], "pdays": [-1, 10],
        "previous": [0, 1], "poutcome": ["unknown", "success"], "duration": [300, 100], "y": ["no", "yes"],
    })


def test_prepare_excludes_duration_and_encodes_target() -> None:
    x, y = prepare_frame(sample_frame())
    assert "duration" not in x.columns
    assert y.tolist() == [0, 1]


def test_full_preprocessor_accepts_raw_rows() -> None:
    x, _ = prepare_frame(sample_frame())
    transformed = build_preprocessor().fit_transform(engineer_features(x))
    assert transformed.shape[0] == 2
    assert transformed.shape[1] > len(x.columns)
