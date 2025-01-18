from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'fire-grind',
    'start_date': datetime(2021, 1, 1),
    'catchup': False,
    # 'depends_on_past': False,
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5)
}

dag = DAG(
  dag_id='hello_world',
  default_args=default_args,
  schedule=timedelta(days=1),
)

t1 = BashOperator(
  task_id='print_hello',
  bash_command='echo "Hello World"',
  dag=dag,
)

t2 = BashOperator(
  task_id='print_date',
  bash_command='date',
  dag=dag,
)

t1 >> t2