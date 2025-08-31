import argparse
import pandas as pd
import json
import csv
import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

current_file = Path(__file__).resolve()
utils_dir = current_file.parent  
evals_dir = utils_dir.parent  
cemig_agent_dir = evals_dir.parent 
agents_dir = cemig_agent_dir.parent  
project_root = agents_dir.parent  

sys.path.insert(0, str(project_root))

try:
    from agents.cemig_agent.tools.connector.database_connector import PostgreSQLConnector
    from agents.cemig_agent.common.config import Config
except ImportError:
    sys.path.insert(0, str(cemig_agent_dir))
    from tools.connector.database_connector import PostgreSQLConnector
    from common.config import Config


class QueryTestGenerator:
    """Classe para gerar dados de teste a partir de queries SQL."""
    
    def __init__(self, connector: PostgreSQLConnector):
        """Inicializa o gerador de testes."""

        self.connector = connector
        self.total_processed = 0
        self.total_errors = 0
    
    def parse_csv(self, csv_file_path: str, delimiter: str = ';') -> pd.DataFrame:
        """Lê o CSV com tratamento adequado para diferentes delimitadores."""
        
        try:
            df = pd.read_csv(
                csv_file_path, 
                delimiter=delimiter,
                encoding='utf-8',
                quoting=csv.QUOTE_ALL,
                escapechar='\\'
            )
            
            if df.empty or len(df.columns) != 3:
                return self._parse_csv_manually(csv_file_path, delimiter)
                
            return df
            
        except Exception as e:
            print(f"Aviso: Pandas falhou ({e}), usando parsing manual...")
            return self._parse_csv_manually(csv_file_path, delimiter)
    
    def _parse_csv_manually(self, csv_file_path: str, delimiter: str) -> pd.DataFrame:
        """Parsing manual como fallback."""
        rows = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row in reader:
                cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                rows.append(cleaned_row)
        
        return pd.DataFrame(rows)
    
    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Valida se o DataFrame tem as colunas necessárias."""

        required_columns = ['table_name', 'query_sql', 'query_lang']
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Colunas obrigatórias não encontradas: {missing}")
        
        print(f"Validação OK: {len(df)} queries encontradas")
        return True
    
    def execute_query_safe(self, query: str) -> List[Dict[str, Any]]:
        """Executa query com tratamento de erro."""

        try:
            results = self.connector.execute_query(query, fetch_all=True)
            return results if results else []
        except Exception as e:
            self.total_errors += 1
            return [{"error": str(e), "query_preview": query[:200]}]
    
    def process_queries(
        self, 
        df: pd.DataFrame, 
        limit: Optional[int] = None,
        verbose: bool = True
    ) -> pd.DataFrame:
        """Processa as queries do DataFrame."""

        results = []
        rows_to_process = min(limit, len(df)) if limit else len(df)
        
        print(f"\n{'='*60}")
        print(f"Processando {rows_to_process} de {len(df)} queries")
        print(f"{'='*60}\n")
        
        for idx, row in df.head(rows_to_process).iterrows():
            self.total_processed += 1
            
            if verbose:
                print(f"[{self.total_processed}/{rows_to_process}] {row['table_name']}", end=" ")
            
            query_result = self.execute_query_safe(row['query_sql'])
            
            result_json = json.dumps(
                query_result, 
                ensure_ascii=False, 
                indent=2,
                default=str  
            )
            results.append(result_json)
            
            if verbose:
                if query_result and isinstance(query_result[0], dict) and "error" in query_result[0]:
                    print("Erro")
                else:
                    print(f"✓ {len(query_result)} registros")
        
        df_result = df.head(rows_to_process).copy()
        df_result['result_expected'] = results
        
        return df_result
    
    def save_results(self, df: pd.DataFrame, output_path: str):
        """Salva DataFrame com resultados em CSV."""

        df.to_csv(
            output_path, 
            index=False, 
            encoding='utf-8', 
            quoting=csv.QUOTE_ALL,
            escapechar='\\'
        )
        print(f"\nArquivo salvo: {output_path}")
        print(f"Total processado: {self.total_processed}")
        print(f"Total com erros: {self.total_errors}")
    
    def generate_test_files(self, input_csv: str, output_csv: str, preview: Optional[int] = None):
        """Método principal para gerar arquivos de teste."""

        try:
            if not os.path.exists(input_csv):
                raise FileNotFoundError(f"Arquivo não encontrado: {input_csv}")
            
            print("Conectando ao banco de dados...")
            if not self.connector.connect():
                raise ConnectionError("Falha ao conectar ao banco de dados")
            print("Conectado com sucesso\n")
            
            print(f"Lendo arquivo: {input_csv}")
            df = self.parse_csv(input_csv)
            self.validate_dataframe(df)
            
            df_results = self.process_queries(df, limit=preview, verbose=True)
            
            self.save_results(df_results, output_csv)
            
            if preview:
                remaining = len(df) - preview
                if remaining > 0:
                    print(f"\nModo preview: {remaining} queries não processadas")
                    print(f"Para processar todas, remova o flag --preview")
            
        except Exception as e:
            print(f"\nErro: {e}")
            sys.exit(1)
        finally:
            if self.connector.connection:
                self.connector.close()
                print("\nConexão fechada")


def main():
    """Função principal com parsing de argumentos."""
    parser = argparse.ArgumentParser(
        description='Gera arquivos de teste executando queries SQL de um CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s queries.csv results.csv
  %(prog)s queries.csv results.csv --preview 10
  %(prog)s input.csv output.csv --delimiter ","
        """
    )
    
    parser.add_argument(
        'input_csv',
        help='Arquivo CSV de entrada com as queries'
    )
    parser.add_argument(
        'output_csv',
        help='Arquivo CSV de saída com os resultados'
    )
    
    parser.add_argument(
        '--preview',
        type=int,
        metavar='N',
        help='Processar apenas N queries (modo preview)'
    )
    parser.add_argument(
        '--delimiter',
        default=';',
        help='Delimitador do CSV (padrão: ";")'
    )
    parser.add_argument(
        '--host',
        default=None,
        help='Override do host do banco (usa Config se não especificado)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Override da porta do banco (usa Config se não especificado)'
    )
    
    args = parser.parse_args()
    
    try:
        db_config = {
            'host': args.host or Config.POSTGRES_HOST,
            'port': args.port or Config.POSTGRES_PORT,
            'database': Config.POSTGRES_DATABASE,
            'user': Config.POSTGRES_USER,
            'password': Config.POSTGRES_PASSWORD,
        }
        
        print(f"Configuração do banco:")
        print(f"Host: {db_config['host']}")
        print(f"Port: {db_config['port']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}")
        print()
        
        connector = PostgreSQLConnector(**db_config)
        
        generator = QueryTestGenerator(connector)
        generator.generate_test_files(
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            preview=args.preview
        )
        
    except AttributeError as e:
        print(f"Erro de configuração: {e}")
        print("\nVerifique se as variáveis de ambiente estão configuradas:")
        print("export POSTGRES_HOST=seu_host")
        print("export POSTGRES_PORT=5435")
        print("export POSTGRES_DATABASE=seu_database")
        print("export POSTGRES_USER=seu_usuario")
        print("export POSTGRES_PASSWORD=sua_senha")
        print("\nOu use um arquivo .env na raiz do projeto")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()