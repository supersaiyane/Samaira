import pytest
from airflow.models import DagBag

def test_dag_integrity():
    dag_bag = DagBag(dag_folder="airflow/dags", include_examples=False)
    assert "cost_forecasting_v3" in dag_bag.dags
    dag = dag_bag.get_dag("cost_forecasting_v3")
    assert dag.default_args["retries"] == 1
    assert dag.schedule_interval == "@daily"
