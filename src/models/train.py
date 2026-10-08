"""Train candidate models, track metrics in MLflow, and serialize the winning pipeline."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import mlflow
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, precision_score, recall_score,
                             roc_auc_score, RocCurveDisplay, PrecisionRecallDisplay)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sqlalchemy import create_engine, text
from xgboost import XGBClassifier

from src.config import DATA_PATH, DATABASE_URL, MLFLOW_TRACKING_URI, MODEL_PATH, RANDOM_STATE, TARGET
from src.data.preprocessing import build_preprocessor, prepare_frame
from src.features.engineering import engineer_features

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def load_training_data() -> pd.DataFrame:
    """Load the persisted raw dataset from PostgreSQL."""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        return pd.read_sql(text("SELECT * FROM bank_marketing.raw_customers"), connection)


def candidate_models() -> dict[str, Any]:
    """Return the required baseline and tree-based classifiers."""
    return {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=250, class_weight="balanced_subsample", min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE),
        "xgboost": XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.85, colsample_bytree=0.85, eval_metric="logloss", scale_pos_weight=8, n_jobs=4, random_state=RANDOM_STATE),
    }


def train_and_register(frame: pd.DataFrame) -> dict[str, Any]:
    """Compare candidates, log evaluations, and serialize the selected full pipeline."""
    x, y = prepare_frame(frame)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("bank-marketing-subscription")
    results: list[dict[str, Any]] = []
    best_pipeline: Pipeline | None = None
    best_score = -1.0
    best_metrics: dict[str, float] = {}
    best_name = ""
    for name, classifier in candidate_models().items():
        pipeline = Pipeline([
            ("feature_engineering", FunctionTransformer(engineer_features, validate=False)),
            ("preprocessing", build_preprocessor()),
            ("classifier", classifier),
        ])
        with mlflow.start_run(run_name=name) as run:
            pipeline.fit(x_train, y_train)
            probabilities = pipeline.predict_proba(x_test)[:, 1]
            predictions = (probabilities >= 0.5).astype(int)
            metrics = {
                "accuracy": accuracy_score(y_test, predictions),
                "precision": precision_score(y_test, predictions, zero_division=0),
                "recall": recall_score(y_test, predictions, zero_division=0),
                "f1": f1_score(y_test, predictions, zero_division=0),
                "roc_auc": roc_auc_score(y_test, probabilities),
            }
            from sklearn.metrics import confusion_matrix

            tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
            metrics.update({"true_negative": int(tn), "false_positive": int(fp), "false_negative": int(fn), "true_positive": int(tp)})
            mlflow.log_metrics(metrics)
            mlflow.log_params({"model": name, "threshold": 0.5, "features": len(x.columns)})
            for filename, display_type in (("roc_curve.png", RocCurveDisplay), ("precision_recall_curve.png", PrecisionRecallDisplay)):
                figure, axis = plt.subplots()
                display_type.from_predictions(y_test, probabilities, ax=axis)
                figure.tight_layout()
                figure.savefig(filename)
                mlflow.log_artifact(filename, artifact_path="evaluation")
                plt.close(figure)
                Path(filename).unlink(missing_ok=True)
            if hasattr(classifier, "feature_importances_"):
                names = pipeline.named_steps["preprocessing"].get_feature_names_out()
                importance = classifier.feature_importances_
                top = sorted(zip(names, importance), key=lambda pair: pair[1], reverse=True)[:15]
                figure, axis = plt.subplots(figsize=(8, 5))
                axis.barh([item[0] for item in reversed(top)], [item[1] for item in reversed(top)])
                axis.set_title(f"Top feature importances — {name}")
                figure.tight_layout()
                figure.savefig("feature_importance.png")
                mlflow.log_artifact("feature_importance.png", artifact_path="evaluation")
                plt.close(figure)
                Path("feature_importance.png").unlink(missing_ok=True)
            mlflow.sklearn.log_model(pipeline, artifact_path="pipeline", registered_model_name="bank-marketing-classifier")
            results.append({"model": name, **metrics, "run_id": run.info.run_id})
            # ROC-AUC leads selection; F1 breaks ties and highlights the positive-class trade-off.
            score = metrics["roc_auc"] + metrics["f1"] * 1e-3
            if score > best_score:
                best_score, best_pipeline, best_metrics, best_name = score, pipeline, metrics, name
    if best_pipeline is None:
        raise RuntimeError("Aucun modèle n'a pu être entraîné")
    output = Path(MODEL_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, output)
    output.with_suffix(".json").write_text(json.dumps({"model": best_name, "metrics": best_metrics}, indent=2), encoding="utf-8")
    LOGGER.info("Pipeline %s sérialisé vers %s", best_name, output)
    return {"model": best_name, "metrics": best_metrics, "candidates": results, "model_path": str(output)}


def main() -> None:
    """Train from the PostgreSQL raw table."""
    frame = load_training_data()
    summary = train_and_register(frame)
    LOGGER.info("Résultats : %s", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
