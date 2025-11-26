# YouTube Engagement Optimizer  
  
Analyze YouTube videos and Shorts to identify what content drives maximum engagement and generate data‑driven recommendations for future content. This mini‑app simulates a production‑grade data platform with ingestion, analysis, orchestration and recommendation components.  
  
## 📊 Architecture Overview  
  
```
    +----------------------+        +----------------------+        +----------------------+  
    |  Ingestion Layer     | ---->  |  Storage (Bronze)    | ---->  |  Analytics & Recs    |  
    |  (YouTube Data API)  |        |  Raw CSV/Parquet     |        |  Compute Engagement   |  
    +----------------------+        +----------------------+        +----------------------+  
             |                                 ^                               |  
             |                                 |                               |  
             v                                 |                               v  
    Airflow DAG orchestrates all steps  ------ + ------>  Suggestions (topics, formats)  
```  
  
- **Ingestion**: Pulls recent videos and their statistics from the YouTube Data API for a given channel. The script `ingestion/yt_data_ingest.py` writes raw metadata and stats to CSV for downstream consumption.  
- **Storage**: Raw data is stored in a lake‑like structure (bronze). Future enhancements could use Delta Lake or Iceberg.  
- **Analytics**: The module `analysis/engagement_analysis.py` loads raw data, computes a composite engagement score (based on views, likes, comments, shares and watch‑time), classifies content as video vs. short, and ranks videos by engagement.  
- **Recommendations**: The analytics module extracts the most frequent tags among top‑performing videos to suggest topics that are likely to resonate with audiences.  
- **Orchestration**: An Airflow DAG (placeholder `dags/youtube_pipeline_dag.py`) can be used to schedule ingestion and analysis tasks on a regular cadence (e.g., daily).  
  
## 📁 Repository Structure  
  
- `ingestion/yt_data_ingest.py` – Fetches recent YouTube videos and their statistics via the YouTube Data API.  
- `analysis/engagement_analysis.py` – Computes engagement scores, classifies content, ranks videos, and suggests topics.  
- `dags/` – (Placeholder) Airflow DAG to orchestrate ingestion and analysis.  
- `README.md` – Project overview, architecture diagram and usage instructions.  
  
## 🚀 Getting Started  
  
1. **Clone the repository**    
   ```  
   git clone https://github.com/shaleenswarup/youtube-engagement-optimizer.git  
   cd youtube-engagement-optimizer  
   ```  
2. **Install dependencies**    
   Create a virtual environment and install required packages:  
   ```  
   python -m venv .venv  
   source .venv/bin/activate  
   pip install pandas google-api-python-client apache-airflow  
   ```  
3. **Set up API keys**    
   Obtain a YouTube Data API key and set it in your environment:  
   ```  
   export YOUTUBE_API_KEY='YOUR_API_KEY'  
   ```  
4. **Run ingestion**    
   Fetch recent videos from a channel and save them to a CSV file:  
   ```  
   python ingestion/yt_data_ingest.py --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw --output-path data/videos.csv --max-results 50  
   ```  
5. **Run analysis**    
   Compute engagement scores and see top videos and suggested topics:  
   ```  
   python analysis/engagement_analysis.py --input-path data/videos.csv  
   ```  
6. **Run the Airflow DAG (optional)**    
   - Install and initialize Airflow (`pip install apache-airflow` and run `airflow db init`).    
   - Copy a DAG script into the `~/airflow/dags` directory (you can create a DAG under `dags/` that imports the ingestion and analysis functions).    
   - Start the Airflow webserver and scheduler (`airflow webserver -p 8080` and `airflow scheduler`).    
   - Trigger the `youtube_pipeline` DAG from the Airflow UI.  
  
## 🧱 Extending the Project  
  
- Add support for streaming ingestion using Kafka and Spark Structured Streaming.  
- Store raw and processed data in a Lakehouse (Delta Lake or Iceberg) for ACID properties and efficient analytics.  
- Integrate a web dashboard (e.g., Streamlit) to visualize engagement trends and recommendations.  
- Implement data quality checks with tools like Great Expectations.  
- Set up CI/CD pipelines with GitHub Actions and manage infrastructure using Terraform.  
  
This repository now reflects a complete mini‑app with clear architecture, instructions, and modular code for ingesting and analyzing YouTube content. Feel free to extend it further to suit your needs. 
