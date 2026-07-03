ARG AIRFLOW_IMAGE=apache/airflow:2.10.5-python3.12
FROM ${AIRFLOW_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/airflow/project

USER root
WORKDIR /opt/airflow/project

COPY pyproject.toml README.md ./
COPY app ./app
COPY airflow ./airflow

RUN chown -R airflow:0 /opt/airflow/project

USER airflow

RUN pip install --no-cache-dir psycopg2-binary \
    && pip install --no-cache-dir .
