"""Daily ingestion and model training workflow."""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine, text

CSV_PATH = "/app/bank/bank-full.csv"


def ingest_csv() -> None:
    """Load the semicolon-separated UCI file into PostgreSQL's raw schema."""
    import os

    frame = pd.read_csv(CSV_PATH, sep=";")
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS bank_marketing"))
    frame.to_sql("raw_customers", engine, schema="bank_marketing", if_exists="replace", index=False, chunksize=2000)


def train_model() -> None:
    """Train, track and serialize the selected sklearn pipeline."""
    from src.models.train import main

    main()


with DAG(
    dag_id="bank_marketing_train",
    description="Ingest UCI Bank Marketing data, train candidates, and export a registered pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@monthly",
    catchup=False,
    default_args={"owner": "data-platform", "retries": 1, "retry_delay": timedelta(minutes=2)},
    tags=["bank-marketing", "ml"],
) as dag:
    ingest = PythonOperator(task_id="ingest_csv_to_postgres", python_callable=ingest_csv)
    train = PythonOperator(task_id="train_compare_register_and_serialize", python_callable=train_model)
    ingest >> train
