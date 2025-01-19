from datetime import datetime, timedelta
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import pandas as pd

def get_data(**kwargs):
    url = 'https://raw.githubusercontent.com/airscholar/ApacheFlink-SalesAnalytics/main/output/new-output.csv'
    response = requests.get(url)

    if response.status_code == 200:
        df = pd.read_csv(url, header=None, names=['Category', 'Price', 'Quantity'])

        #convert dataframe to json string
        json_data = df.to_json(orient='records')

        kwargs['ti'].xcom_push(key='data', value=json_data)
    else:
        raise Exception(f'Failed to fetch data, status code: {response.status_code}')

def preview_data(**kwargs):
    output_data = kwargs['ti'].xcom_pull(key='data', task_ids='get_data')
    print(output_data)
    if output_data:
        output_data = json.loads(output_data)
    else:
        raise ValueError('No data received from xcom')
    
    df = pd.DataFrame(output_data)

    #compute total sales
    df['Total'] = df['Price'] * df['Quantity']

    df = df.groupby('Category', as_index=False).agg({'Quantity': 'sum', 'Total': 'sum'})

    #sort by total sales
    df = df.sort_values(by='Total', ascending=False)

    print(df[['Category', 'Total']].head(20))

default_args = {
    'owner': 'fire-grind',
    'start_date': datetime(2025, 1, 19),
    'catchup': False,
}

dag = DAG(
  dag_id='fetch_and_preview',
  default_args=default_args,
  schedule=timedelta(days=1),
)

get_data_from_url = PythonOperator(
    task_id='get_data',
    python_callable=get_data,
    provide_context=True,
    dag=dag,
)

preview_data_from_url = PythonOperator(
    task_id = 'preview_data',
    python_callable = preview_data,
    dag = dag,
)

get_data_from_url >> preview_data_from_url
