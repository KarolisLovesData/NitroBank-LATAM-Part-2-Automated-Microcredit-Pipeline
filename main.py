import os
import requests
import pandas as pd
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from google.cloud import storage
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

#Used Pydantic to verify data integrity before it even touches my datalake/gt=0 ensures no negative or 0 FX rates
class CurrencyRate(BaseModel):
    base_currency: str = "USD"
    target_currency: str
    rate: float = Field(gt=0)

    @field_validator('target_currency')  # 4. Changed from @validator
    @classmethod
    def validate_currency_code(cls, v):
        return v.upper()

def fetch_latam_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)
    data = response.json()
    latam_currencies = ['COP', 'MXN', 'BRL']
    validated_data = []

    for currency in latam_currencies:
        rate_entry = CurrencyRate(
            target_currency=currency,
            rate=data['rates'].get(currency)
        )
        validated_data.append(rate_entry.model_dump())
    return validated_data

def upload_to_gcs(local_path, bucket_name):
    # Added check for keys.json to support both local and cloud
    if os.path.exists('keys.json'):
        client = storage.Client.from_service_account_json('keys.json')
    else:
        client = storage.Client()
        
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(local_path)

    print(f"☁️ Uploading {local_path} to GCS...")
    blob.upload_from_filename(local_path)
    print(f" Success! Data landed in gs://{bucket_name}/")

def trigger_databricks_workflow():
    db_instance = os.getenv("DATABRICKS_INSTANCE")
    db_token = os.getenv("DATABRICKS_TOKEN")
    job_id = os.getenv("DATABRICKS_JOB_ID")

    if not all([db_instance, db_token, job_id]):
        raise ValueError("❌ Error: Databricks variables missing from .env file!")

    endpoint = f"{db_instance.rstrip('/')}/api/2.1/jobs/run-now"
    headers = {
        "Authorization": f"Bearer {db_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Signaling Databricks Job {job_id}...")
    response = requests.post(endpoint, headers=headers, json={"job_id": job_id})

    if response.status_code == 200:
        run_id = response.json().get("run_id")
        print(f" Databricks is now running! (Run ID: {run_id})")
    else:
        print(f"❌ Failed to wake up Databricks: {response.text}")

if __name__ == "__main__":   #Used to ensure that the code only runs when this script is executed directly# and not when imported as a module.
    
    today = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"fx_rates_{today}.parquet"
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    
    print("   Starting NitroBank Ingestion!  ")
    
    try:
        raw_data = fetch_latam_rates()
        pd.DataFrame(raw_data).to_parquet(filename, index=False)
        upload_to_gcs(filename, bucket_name)
        trigger_databricks_workflow()


    except Exception as e:

        print(f"❌ Pipeline failed: {str(e)}")