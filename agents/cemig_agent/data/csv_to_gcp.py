import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from pathlib import Path
import chardet
from src.config import Config


class CSVToGCP:
    def __init__(self):
        self.config = Config()
        
    def create_database(self):
        """Cria o banco de dados se não existir"""
        conn = psycopg2.connect(**self.config.get_default_connection_params())
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config.DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{self.config.DB_NAME}"')
            print(f"Banco {self.config.DB_NAME} criado")
        else:
            print(f"Banco {self.config.DB_NAME} já existe")
            
        cursor.close()
        conn.close()

    def get_engine(self):
        """Retorna engine do SQLAlchemy"""
        return create_engine(self.config.get_connection_string())

    def clean_table_name(self, filename, folder):
        """Limpa e formata o nome da tabela"""
        table_name = filename.replace('.csv', '')
        table_name = table_name.replace('-', '_')
        table_name = table_name.replace(' ', '_')
        return f"{folder}_{table_name}".lower()

    def detect_encoding(self, file_path):
        """Detecta o encoding do arquivo automaticamente"""
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)
            result = chardet.detect(raw_data)
            return result['encoding']

    def try_read_csv(self, csv_path):
        """Tenta ler o CSV com diferentes métodos"""
        print(f"  Tentando ler: {csv_path}")
        
        # Primeiro, tenta detectar o encoding automaticamente
        try:
            detected_encoding = self.detect_encoding(csv_path)
            print(f"  Encoding detectado: {detected_encoding}")
            if detected_encoding:
                df = pd.read_csv(
                    csv_path, 
                    encoding=detected_encoding,
                    sep=None,
                    engine='python',
                    on_bad_lines='skip'
                )
                print(f"  Sucesso com encoding detectado: {detected_encoding}")
                return df
        except Exception as e:
            print(f"  Falha com encoding detectado: {e}")
        
        #lista de encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16', 'utf-8-sig']
        
        #diferentes seps
        separators = [None, ',', ';', '\t', '|']
        
        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(
                        csv_path, 
                        encoding=encoding,
                        sep=sep,
                        engine='python',
                        on_bad_lines='skip',
                        quoting=3
                    )
                    if len(df.columns) > 1 or len(df) > 0:
                        print(f"  Sucesso - Encoding: {encoding}, Separador: {sep}")
                        return df
                except Exception:
                    continue
        
        #ultimo recurso
        try:
            df = pd.read_table(csv_path, encoding='utf-8', on_bad_lines='skip')
            print("  Sucesso com read_table")
            return df
        except:
            pass
        
        raise Exception("Não foi possível ler o arquivo com nenhum encoding/separador")

    def process_csv(self, csv_path, table_name=None):
        """Processa um arquivo CSV específico"""
        csv_path = Path(csv_path)
        
        if not csv_path.exists():
            print(f"ERRO: Arquivo não encontrado: {csv_path}")
            return False
        
        if not csv_path.is_file():
            print(f"ERRO: O path não é um arquivo: {csv_path}")
            return False
        
        if table_name is None:
            table_name = self.clean_table_name(csv_path.name, csv_path.parent.name)
        
        print(f"Processando: {csv_path}")
        
        try:
            df = self.try_read_csv(csv_path)
            
            # Limpa os nomes das colunas
            df.columns = df.columns.astype(str)
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('-', '_').str.lower()
            
            # Remove valores vazios
            df = df.replace({'': None})
            
            # Conecta ao banco e salva
            engine = self.get_engine()
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
            
            print(f"  SUCESSO: {table_name} ({len(df)} linhas, {len(df.columns)} colunas)")
            engine.dispose()
            return True
            
        except Exception as e:
            print(f"  ERRO ao processar {csv_path.name}: {e}")
            return False

    def process_multiple_csvs(self, csv_paths):
        """Processa múltiplos arquivos CSV"""
        results = {}
        for csv_path in csv_paths:
            results[csv_path] = self.process_csv(csv_path)
        return results

    def run(self, csv_file, table_name=None):
        """Método principal para executar o processo completo"""
        self.create_database()
        return self.process_csv(csv_file, table_name)