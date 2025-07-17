import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional, List, Union

class PostgreSQLConnector:
    """
    Classe para conexão e execução de consultas SQL em um banco de dados 
    PostgreSQL hospedado no Google Cloud SQL usando psycopg2.
    """
    
    def __init__(
        self,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5435,
        use_proxy: bool = False,
        instance_connection_name: Optional[str] = None
    ):
        """
        Inicializa o conector PostgreSQL.
        
        Args:
            host: Endereço do host do banco de dados
            database: Nome do banco de dados
            user: Nome de usuário do banco de dados
            password: Senha do banco de dados
            port: Porta do banco de dados (padrão: 5432)
            use_proxy: Se deve usar o proxy do Cloud SQL (para conexões locais)
            instance_connection_name: Nome da instância do Cloud SQL (formato: project:region:instance)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.use_proxy = use_proxy
        self.instance_connection_name = instance_connection_name
        self.connection = None
        
    def connect(self) -> bool:
        """
        Estabelece conexão com o banco de dados PostgreSQL no Google Cloud SQL.
        
        Returns:
            bool: True se a conexão for bem-sucedida, False caso contrário.
        """
        try:
            if self.use_proxy and self.instance_connection_name:
                connection_params = {
                    'dbname': self.database,
                    'user': self.user,
                    'password': self.password,
                    'host': '/cloudsql/' + self.instance_connection_name,
                }
            else:
                connection_params = {
                    'dbname': self.database,
                    'user': self.user,
                    'password': self.password,
                    'host': self.host,
                    'port': self.port
                }
                
            self.connection = psycopg2.connect(**connection_params)

            self.connection.autocommit = False

            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                
            return True
            
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
            
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None,
        fetch_all: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int, None]:
        """
        Executa uma consulta SQL no banco de dados.
        
        Args:
            query: String contendo a consulta SQL a ser executada
            params: Dicionário com parâmetros para a consulta (opcional)
            fetch_all: Se True, retorna todos os registros; se False, 
                       retorna apenas um registro (útil para SELECT) ou 
                       o número de linhas afetadas (para INSERT/UPDATE/DELETE)
                       
        Returns:
            Lista de dicionários com os resultados da consulta (fetch_all=True),
            Dicionário com um único resultado (fetch_all=False em SELECT),
            Número de linhas afetadas (para INSERT/UPDATE/DELETE) ou
            None em caso de erro
            
        Raises:
            ValueError: Se a conexão não foi estabelecida
            psycopg2.Error: Em caso de erro na execução da consulta
        """
        if not self.connection:
            raise ValueError("Conexão não estabelecida. Execute o método connect() primeiro.")
            
        cursor = None
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, params or {})
            
            is_select = query.lstrip().upper().startswith(("SELECT", "WITH"))
            
            if is_select:
                if fetch_all:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    row = cursor.fetchone()
                    return dict(row) if row else None
            else:
                affected_rows = cursor.rowcount
                self.connection.commit()
                return affected_rows
                
        except psycopg2.Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"Erro ao executar consulta: {str(e)}")
            raise
            
        finally:
            if cursor:
                cursor.close()

    def get_tables_and_columns(self):
        """
        Obtém informações básicas do schema: tabelas, colunas e tipos de dados.
        
        Returns:
            Dict: Dicionário com estrutura de tabelas e suas colunas.
        """
        if not self.connection:
            raise ValueError("Conexão não estabelecida. Execute o método connect() primeiro.")
        
        schema = {}
        
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        tables = self.execute_query(tables_query)
        
        for table in tables:
            table_name = table['table_name']
            schema[table_name] = {}
            
            columns_query = """
                SELECT 
                    column_name, 
                    data_type
                FROM 
                    information_schema.columns
                WHERE 
                    table_schema = 'public' AND table_name = %(table_name)s
                ORDER BY 
                    ordinal_position
            """
            columns = self.execute_query(columns_query, {'table_name': table_name})
            
            for column in columns:
                column_name = column['column_name']
                data_type = column['data_type']
                schema[table_name][column_name] = data_type
        
        return schema
                    
    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
