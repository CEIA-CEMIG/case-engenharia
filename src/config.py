import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5435')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'case-engenharia')
    DB_DEFAULT = os.getenv('DB_DEFAULT', 'postgres')
    
    @classmethod
    def get_connection_string(cls):
        return (
            f"postgresql+psycopg2://{cls.DB_USER}:"
            f"{cls.DB_PASSWORD}@{cls.DB_HOST}:"
            f"{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def get_default_connection_params(cls):
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_DEFAULT
        }