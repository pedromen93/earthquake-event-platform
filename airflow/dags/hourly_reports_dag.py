"""Airflow DAG for consolidated hourly earthquake reports."""

from __future__ import annotations

from datetime import datetime, timedelta
from importlib import import_module, util
from typing import Any


def _load_airflow_dependencies() -> tuple[Any, Any]:
    """Load Airflow objects dynamically when the package is available."""

    if util.find_spec("airflow") is None:
        return None, None

    dag_class = import_module("airflow").DAG
    python_operator = import_module("airflow.operators.python").PythonOperator
    return dag_class, python_operator


def _run_hourly_report_task(data_interval_start: str | None = None, **_: Any) -> None:
    """Delegate hourly report generation to the application runner."""

    from datetime import datetime

    from app.workers.reporting.main import run_sync

    report_date = datetime.fromisoformat(data_interval_start) if data_interval_start else None
    run_sync(report_date=report_date)


DAG, PythonOperator = _load_airflow_dependencies()

if DAG is not None and PythonOperator is not None:
    default_args = {
        "owner": "earthquake-platform",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        dag_id="earthquake_hourly_reports",
        description="Generate consolidated hourly earthquake reports.",
        default_args=default_args,
        schedule="0 * * * *",
        start_date=datetime(2026, 6, 24),
        catchup=False,
        tags=["earthquakes", "reporting"],
    ) as dag:
        generate_hourly_report = PythonOperator(
            task_id="generate_hourly_report",
            python_callable=_run_hourly_report_task,
            op_kwargs={"data_interval_start": "{{ data_interval_start.isoformat() }}"},
        )
