import pandas as pd
import psycopg2
import json
from psycopg2.extras import RealDictCursor
import sys
import csv
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class PostgreSQLQueryProcessor:
    def __init__(self):
        self.db_config = {
            'host': Config.POSTGRES_HOST,  
            'port': Config.POSTGRES_PORT,
            'user': Config.POSTGRES_USER,
            'password': Config.POSTGRES_PASSWORD,
            'database': Config.POSTGRES_DATABASE,
        }
        self.connection = None
    
    def connect_to_db(self):
        """Conecta ao banco PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            print("Conectado ao PostgreSQL com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            return False
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Executa uma query e retorna os resultados como lista de dicionários"""
        if not self.connection:
            raise Exception("Não conectado ao banco de dados")
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
                results_list = []
                for row in results:
                    row_dict = {}
                    for key, value in row.items():
                        if isinstance(value, (int, float, str, bool)) or value is None:
                            row_dict[key] = value
                        else:
                            row_dict[key] = str(value)
                    results_list.append(row_dict)
                
                return results_list
        
        except Exception as e:
            print(f"Erro ao executar query: {e}")
            return [{"error": str(e), "query_preview": query[:200]}]
    
    def read_csv_properly(self, csv_file_path: str):
        """Lê o CSV lidando corretamente com vírgulas dentro dos campos"""        
        try:
            return self.parse_custom_csv(csv_file_path)
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            raise Exception(f"Não foi possível ler o CSV: {e}")
    
    def parse_custom_csv(self, csv_file_path: str):
        """Parsing customizado para CSV com ponto e vírgula como delimitador"""
        rows = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        headers = ['table_name', 'query_sql', 'query_lang']
        print(f"Cabeçalhos: {headers}")
        
        for i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split(';')
                
                if len(parts) != 3:
                    print(f"Linha {i}: Esperado 3 campos, encontrado {len(parts)}")
                    continue
                
                table_name = parts[0].strip()
                query_sql = parts[1].strip()
                query_lang = parts[2].strip()
                
                rows.append({
                    'table_name': table_name,
                    'query_sql': query_sql,
                    'query_lang': query_lang
                })
                
                if i <= 5:  
                    print(f"Linha {i} processada:")
                    print(f"Tabela: {table_name}")
                    print(f"Query: {query_sql[:60]}...")
                    print(f"Descrição: {query_lang[:60]}...")
                    print()
                    
            except Exception as e:
                print(f"Erro ao processar linha {i}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        print(f"CSV processado: {len(df)} linhas")
        return df
    
    def validate_dataframe(self, df):
        """Valida se o DataFrame tem as colunas necessárias"""
        required_columns = ['table_name', 'query_sql', 'query_lang']
        
        print(f"Dimensões do DataFrame: {df.shape}")
        print(f"Colunas encontradas: {list(df.columns)}")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise Exception(f"Colunas obrigatórias não encontradas: {missing_columns}")
        
        print(f"\nPreview dos primeiros registros:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"\nRegistro {i+1}:")
            print(f"Tabela: {row['table_name']}")
            print(f"Query: {row['query_sql'][:100]}...")
            print(f"Descrição: {row['query_lang'][:100]}...")
        
        return True
    
    def process_csv(self, csv_file_path: str, output_file_path: str = None):
        """Processa o CSV executando as queries e adicionando resultados"""
        try:
            df = self.read_csv_properly(csv_file_path)
            self.validate_dataframe(df)
            
            if not self.connect_to_db():
                return
            
            results = []

            for index, row in df.iterrows():
                table_name = row['table_name']
                query_sql = row['query_sql']
                query_lang = row['query_lang']
                
                print(f"\nProcessando linha {index + 1}/{len(df)}")
                print(f"Tabela: {table_name}")
                print(f"Query: {query_sql[:150]}...")
                
                query_result = self.execute_query(query_sql)
                
                result_json = json.dumps(query_result, ensure_ascii=False, indent=2)
                results.append(result_json)
                
                if "error" in query_result[0] if query_result else False:
                    print(f"Erro na query")
                else:
                    print(f"Query executada. Resultados: {len(query_result)} registros")
            
            df['result_expected'] = results
            
            if output_file_path is None:
                output_file_path = csv_file_path.replace('.csv', '_with_results.csv')
            
            df.to_csv(output_file_path, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
            print(f"\nArquivo salvo: {output_file_path}")
            
        except Exception as e:
            print(f"Erro ao processar CSV: {e}")
        
        finally:
            if self.connection:
                self.connection.close()
                print("Conexão com o banco fechada")
    
    def preview_results(self, csv_file_path: str, num_queries: int = 2):
        """Executa apenas algumas queries para preview dos resultados"""
        try:
            df = self.read_csv_properly(csv_file_path)
            self.validate_dataframe(df)
            
            if not self.connect_to_db():
                return
            
            for index in range(min(num_queries, len(df))):
                row = df.iloc[index]
                print(f"\nPreview Query {index + 1}:")
                print("-" * 50)
                
                result = self.execute_query(row['query_sql'])
                
                if result and "error" not in result[0]:
                    print(f"Sucesso! {len(result)} registros retornados")
                    print(f"Primeiros 3 registros:")
                    for i, record in enumerate(result[:3]):
                        print(f"  {i+1}: {record}")
                    
                    if len(result) > 3:
                        print(f"  ... e mais {len(result) - 3} registros")
                else:
                    print(f"Erro na execução")
                    if result:
                        print(f"Detalhes: {result[0].get('error', 'Erro desconhecido')}")
        
        except Exception as e:
            print(f"Erro no preview: {e}")
        
        finally:
            if self.connection:
                self.connection.close()
                print("Conexão fechada")

def main():
    processor = PostgreSQLQueryProcessor()
    
    csv_file_path = "queries.csv"  
    
    print("Iniciando processamento das queries PostgreSQL")
    print("=" * 60)
    
    print("🔍 Fazendo preview das primeiras 2 queries...")
    processor.preview_results(csv_file_path, num_queries=2)
    
    print("\n" + "=" * 60)
    print("Para processar TODAS as queries, descomente a linha abaixo:")
    print("processor.process_csv(csv_file_path)")
    
    processor.process_csv(csv_file_path)

if __name__ == "__main__":
    main()