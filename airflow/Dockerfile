FROM apache/airflow:2.10.5-python3.11
ARG AIRFLOW_VERSION=2.10.5
USER airflow
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.11.txt" \
    pandas scikit-learn xgboost==2.1.4 mlflow==2.20.3 psycopg2-binary==2.9.10 joblib==1.4.2 matplotlib
RUN pip install --no-cache-dir --no-deps numpy==1.26.4 scikit-learn==1.5.2
USER root
COPY src /opt/airflow/src
ENV PYTHONPATH=/opt/airflow
USER airflow
