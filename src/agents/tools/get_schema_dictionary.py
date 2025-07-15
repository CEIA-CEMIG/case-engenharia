import PyPDF2
import io
import re
from typing import Optional



def read_pdf_to_markdown(pdf_path: str) -> str:
   try:
       with open(pdf_path, 'rb') as file:
           pdf_reader = PyPDF2.PdfReader(file)
           markdown_content = []
           
           full_text = ""
           for page in pdf_reader.pages:
               full_text += page.extract_text() + "\n"
           
           markdown_content = process_structured_document(full_text)
           return markdown_content
           
   except FileNotFoundError:
       return f"# Erro\n\nArquivo não encontrado: {pdf_path}"
   except Exception as e:
       return f"# Erro\n\nErro ao ler o PDF: {str(e)}"

def process_structured_document(text: str) -> str:
   lines = text.split('\n')
   processed_lines = []
   
   in_table = False
   table_headers = []
   table_rows = []
   
   for i, line in enumerate(lines):
       line = line.strip()
       if not line:
           continue
           
       if is_main_title(line):
           if in_table:
               processed_lines.extend(format_table(table_headers, table_rows))
               in_table = False
               table_headers = []
               table_rows = []
           processed_lines.append(f"# {line}\n")
           
       elif is_section_title(line):
           if in_table:
               processed_lines.extend(format_table(table_headers, table_rows))
               in_table = False
               table_headers = []
               table_rows = []
           processed_lines.append(f"## {line}\n")
           
       elif is_subsection_title(line):
           if in_table:
               processed_lines.extend(format_table(table_headers, table_rows))
               in_table = False
               table_headers = []
               table_rows = []
           processed_lines.append(f"### {line}\n")
           
       elif is_table_header(line, i, lines):
           if in_table:
               processed_lines.extend(format_table(table_headers, table_rows))
           table_headers = extract_table_headers(line, i, lines)
           table_rows = []
           in_table = True
           
       elif in_table and is_table_row(line):
           row_data = extract_table_row(line, i, lines)
           if row_data:
               table_rows.append(row_data)
               
       elif is_key_value_pair(line):
           key, value = extract_key_value(line)
           processed_lines.append(f"**{key}**: {value}\n")
           
       elif is_list_item(line):
           processed_lines.append(f"- {line[1:].strip()}")
           
       else:
           if in_table:
               processed_lines.extend(format_table(table_headers, table_rows))
               in_table = False
               table_headers = []
               table_rows = []
           processed_lines.append(line)
   
   if in_table:
       processed_lines.extend(format_table(table_headers, table_rows))
   
   return '\n'.join(processed_lines)

def is_main_title(text: str) -> bool:
   main_titles = ["Dicionário de Metadados", "Conjunto de Dados", "Metadados", "Detalhamento dos campos"]
   return any(title in text for title in main_titles) and len(text) < 100

def is_section_title(text: str) -> bool:
   section_titles = ["Visão Geral", "Catálogo origem", "Órgão responsável", "Categorias no VCGE", "Palavras-chave", "Frequência de atualização"]
   return any(title in text for title in section_titles)

def is_subsection_title(text: str) -> bool:
   return (text.endswith(":") or text.isupper()) and len(text) < 80 and not is_key_value_pair(text)

def is_table_header(line: str, index: int, lines: list) -> bool:
   table_indicators = ["Nome do Campo", "Tipo do dado", "Tamanho"]
   return any(indicator in line for indicator in table_indicators)

def extract_table_headers(line: str, index: int, lines: list) -> list:
   if "Nome do Campo" in line:
       return ["Nome do Campo", "Tipo do dado", "Tamanho do Campo", "Descrição"]
   return []

def is_table_row(line: str) -> bool:
   data_types = ["Data Simples", "Cadeia de Caracteres", "Numérico"]
   return any(dtype in line for dtype in data_types) or re.match(r'^[A-Z][a-zA-Z0-9_]+\s', line)

def extract_table_row(line: str, index: int, lines: list) -> list:
   if "Data Simples" in line:
       parts = line.split("Data Simples")
       if len(parts) >= 2:
           field_name = parts[0].strip()
           description = parts[1].strip()
           return [field_name, "Data Simples", "-", description]
   
   elif "Cadeia de Caracteres" in line:
       parts = line.split("Cadeia de Caracteres")
       if len(parts) >= 2:
           field_name = parts[0].strip()
           rest = parts[1].strip()
           size_match = re.match(r'^(\d+)\s*(.*)', rest)
           if size_match:
               size = size_match.group(1)
               description = size_match.group(2).strip()
               return [field_name, "Cadeia de Caracteres", size, description]
   
   elif "Numérico" in line:
       parts = line.split("Numérico")
       if len(parts) >= 2:
           field_name = parts[0].strip()
           rest = parts[1].strip()
           size_match = re.match(r'^([\d,]+)\s*(.*)', rest)
           if size_match:
               size = size_match.group(1)
               description = size_match.group(2).strip()
               return [field_name, "Numérico", size, description]
   
   return []

def format_table(headers: list, rows: list) -> list:
   if not headers or not rows:
       return []
   
   result = []
   result.append("| " + " | ".join(headers) + " |")
   result.append("| " + " | ".join(["---"] * len(headers)) + " |")
   
   for row in rows:
       if len(row) == len(headers):
           result.append("| " + " | ".join(row) + " |")
   
   result.append("")
   return result

def is_key_value_pair(line: str) -> bool:
   return ":" in line and not line.endswith(":") and len(line.split(":")) == 2

def extract_key_value(line: str) -> tuple:
   parts = line.split(":", 1)
   return parts[0].strip(), parts[1].strip()

def is_list_item(line: str) -> bool:
   return line.startswith(('•', '-', '*', '·'))

def get_schema_dictionary(pdf_path: str) -> str:
   return read_pdf_to_markdown(pdf_path)
