from .connector.database_connector import PostgreSQLConnector
from ..common.config import Config

def execute_sql_query(query_sql: str): 
    """String contendo a consulta SQL a ser executada."""
    
    db_config = {
        "host": Config.POSTGRES_HOST,
        "database": Config.POSTGRES_DATABASE,
        "user": Config.POSTGRES_USER,
        "password": Config.POSTGRES_PASSWORD,
        "port": Config.POSTGRES_PORT
    }

    #print(f'DB Config: {db_config}')
    db = PostgreSQLConnector(**db_config)
    
    try:
        if db.connect():
            resultados = db.execute_query(query_sql)
            
            #print(f'Resultado do banco de dados: {resultados}')
            return resultados
        else:
            return "Erro: Não foi possível conectar ao banco de dados"
            
    except Exception as e:
        return f"Erro ao executar consulta SQL: {str(e)}"
        
    finally:
        db.close()

