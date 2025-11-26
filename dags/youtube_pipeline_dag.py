"""
Airflow DAG to orchestrate YouTube data ingestion and engagement analysis.

This DAG runs daily, executes the ingestion script to pull YouTube data and then runs the analysis script to compute engagement metrics.

To enable this DAG:
- Install Apache Airflow and ensure BashOperator is available.
- Set the environment variable `YOUTUBE_API_KEY` in Airflow variables.
- Replace `$YOUTUBE_CHANNEL_ID` with your target channel ID.

"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    "owner": "data_engineer",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2025, 1, 1),
}

# Define the DAG
with DAG(
    dag_id="youtube_engagement_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    description="Daily pipeline for YouTube data ingestion and engagement analysis",
) as dag:

    # Task: Ingest YouTube data
    ingest = BashOperator(
        task_id="ingest_youtube_data",
        bash_command="python ingestion/yt_data_ingest.py --channel-id $YOUTUBE_CHANNEL_ID --max-results 50 --output-path data/raw_videos.csv",
        env={"YOUTUBE_API_KEY": "{{ var.value.YOUTUBE_API_KEY }}"},
    )

    # Task: Analyze engagement
    analyze = BashOperator(
        task_id="analyze_engagement",
        bash_command="python analysis/engagement_analysis.py --input-path data/raw_videos.csv --output-path data/analysis_output.csv",
    )

    # Set task dependencies
    ingest >> analyze
