"""Feature engineering with campaign-domain rationale."""
from __future__ import annotations

import pandas as pd


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create transparent pre-call features; avoid call duration, which is post-outcome leakage."""
    result = frame.copy()
    if "age" in result:
        result["age_band"] = pd.cut(result["age"], [0, 25, 35, 50, 65, 120], labels=False).fillna(-1).astype(int)
    if "previous" in result:
        result["previously_contacted"] = (result["previous"].fillna(0) > 0).astype("int8")
    if "pdays" in result:
        result["previous_contact_known"] = (result["pdays"] >= 0).astype("int8")
    return result
