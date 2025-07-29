import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', '172.28.0.3')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE', 'case-engenharia')
    POSTGRES_DEFAULT_DB = os.getenv('POSTGRES_DEFAULT_DB', 'postgres')
    POSTGRES_INSTANCE_CONNECTION_NAME = os.getenv('POSTGRES_INSTANCE_CONNECTION_NAME', 'ufg-prd-energygpt:us-central1:your-instance-name')

    # Google Cloud Configuration
    GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "ufg-prd-energygpt")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")