from typing import List, Dict, Any, Optional
from ..common.config import Config

from .connector.database_connector import PostgreSQLConnector

def get_schema_db():
    """Retorna o esquema do banco de dados PostgreSQL."""

    db_config = {
        "host": Config.POSTGRES_HOST,
        "database": Config.POSTGRES_DATABASE,
        "user": Config.POSTGRES_USER,
        "password": Config.POSTGRES_PASSWORD,
        "port": Config.POSTGRES_PORT
    }

    db = PostgreSQLConnector(**db_config)

    try:
        if db.connect():
            shema = db.get_tables_and_columns()
            return str(shema) 
        else:
            return "Erro ao conectar ao banco de dados."
    except Exception as e:
        return f"Erro ao obter o esquema do banco de dados: {str(e)}"
    
    
    