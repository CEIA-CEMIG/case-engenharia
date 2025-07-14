from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

_config_instance = None

class Config:
    """Base configuration class with common settings"""
    APP_NAME = os.getenv("APP_NAME", "MyApp")

    POSTGRES_DATABASE = os.getenv("POSTGRES_DB", "case-engenharia")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "seu_usuario")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sua_senha")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5435"))

    POSTGRES_DEFAULT_DB = os.getenv("POSTGRES_DEFAULT_DB", "postgres")

    GOOGLE_GENAI_USE_VERTEXAI= os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "ufg-prd-energygpt")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")