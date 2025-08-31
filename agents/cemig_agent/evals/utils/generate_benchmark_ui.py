import json
import os
import glob
import re
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


def extract_test_number(filename: str) -> int:
    """Extrai o número do teste do nome do arquivo."""
    match = re.search(r'response_test_(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def process_single_test_file(file_path: str, case_number: int) -> Tuple[List[Dict], int]:
    """Processa um único arquivo de teste."""
    eval_cases = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "eval_cases" in data:
            for idx, eval_case in enumerate(data["eval_cases"], 1):
                clean_case = {
                    "eval_id": f"case{case_number:02d}",
                    "conversation": [],
                    "session_input": eval_case.get("session_input", {
                        "app_name": "cemig_agent",
                        "user_id": "test_user",
                        "state": {}
                    })
                }
                
                for conv in eval_case.get("conversation", []):
                    clean_conv = {
                        "invocation_id": conv.get("invocation_id", f"test-{case_number:03d}"),
                        "user_content": conv.get("user_content", {}),
                        "final_response": conv.get("final_response", {})
                    }
                    clean_case["conversation"].append(clean_conv)
                
                eval_cases.append(clean_case)
                case_number += 1
        
        elif "invocation_id" in data or "user_content" in data:
            clean_case = {
                "eval_id": f"case{case_number:02d}",
                "conversation": [
                    {
                        "invocation_id": data.get("invocation_id", f"test-{case_number:03d}"),
                        "user_content": data.get("user_content", {}),
                        "final_response": data.get("final_response", {})
                    }
                ],
                "session_input": data.get("session_input", {
                    "app_name": "cemig_agent",
                    "user_id": "test_user",
                    "state": {}
                })
            }
            eval_cases.append(clean_case)
            case_number += 1
        
        elif "conversation" in data:
            clean_case = {
                "eval_id": f"case{case_number:02d}",
                "conversation": [],
                "session_input": data.get("session_input", {
                    "app_name": "cemig_agent",
                    "user_id": "test_user",
                    "state": {}
                })
            }
            
            for conv in data.get("conversation", []):
                clean_conv = {
                    "invocation_id": conv.get("invocation_id", f"test-{case_number:03d}"),
                    "user_content": conv.get("user_content", {}),
                    "final_response": conv.get("final_response", {})
                }
                clean_case["conversation"].append(clean_conv)
            
            eval_cases.append(clean_case)
            case_number += 1
        
        else:
            print(f"Aviso: Formato não reconhecido em {file_path}")
            
    except json.JSONDecodeError as e:
        print(f"Erro JSON em {file_path}: {e}")
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
    
    return eval_cases, case_number


def concatenate_test_files(input_dir: str, output_file: str) -> bool:
    """Concatena múltiplos arquivos de teste em um único benchmark."""

    if not os.path.exists(input_dir):
        print(f"Erro: Diretório '{input_dir}' não existe.")
        print(f"  Criando diretório...")
        os.makedirs(input_dir, exist_ok=True)
        print(f"  Diretório criado. Adicione arquivos de teste e execute novamente.")
        return False

    patterns = [
        os.path.join(input_dir, "response_test_*.test.json"),
        os.path.join(input_dir, "response_test_*.json")
    ]
    
    test_files = []
    for pattern in patterns:
        test_files.extend(glob.glob(pattern))
    
    test_files = list(set(test_files))
    test_files.sort(key=lambda x: extract_test_number(os.path.basename(x)))
    
    if not test_files:
        print(f"Nenhum arquivo de teste encontrado em {input_dir}")
        print(f"  Procurando por: response_test_*.json ou response_test_*.test.json")
        return False
    
    print(f"Encontrados {len(test_files)} arquivos de teste")
    print("")

    benchmark = {
        "eval_set_id": "teste_benchmark",
        "name": "teste_benchmark",
        "description": None,
        "eval_cases": []
    }
    
    case_counter = 1
    
    for idx, file_path in enumerate(test_files, 1):
        filename = os.path.basename(file_path)
        print(f"  [{idx:2d}/{len(test_files)}] Processando: {filename}")
        
        eval_cases, case_counter = process_single_test_file(file_path, case_counter)
        benchmark["eval_cases"].extend(eval_cases)
    
    import time
    current_timestamp = time.time()
    for case in benchmark["eval_cases"]:
        if "creation_timestamp" not in case:
            case["creation_timestamp"] = current_timestamp
    
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark, f, indent=2, ensure_ascii=False)
        
        print("")
        print(f"Arquivo criado: '{output_file}'")
        print(f"  Total de casos: {len(benchmark['eval_cases'])}")
        
        total_conversations = sum(len(case.get("conversation", [])) for case in benchmark["eval_cases"])
        print(f"  Total de conversas: {total_conversations}")
        
        print("")
        print("Amostra dos casos criados:")
        for case in benchmark["eval_cases"][:3]:
            user_msg = ""
            if case.get("conversation") and case["conversation"][0].get("user_content"):
                parts = case["conversation"][0]["user_content"].get("parts", [])
                if parts and parts[0].get("text"):
                    text = parts[0]["text"]
                    user_msg = text[:60] + "..." if len(text) > 60 else text
            print(f"  • {case['eval_id']}: {user_msg}")
        
        if len(benchmark["eval_cases"]) > 3:
            print(f"  ... e mais {len(benchmark['eval_cases']) - 3} casos")
        
        return True
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_output(output_file: str) -> bool:
    """Valida o arquivo de benchmark gerado."""
    try:
        if not os.path.exists(output_file):
            print(f"Arquivo '{output_file}' não encontrado")
            return False
            
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Validando '{output_file}':")
        print(f"  • eval_set_id: {data.get('eval_set_id', 'N/A')}")
        print(f"  • name: {data.get('name', 'N/A')}")
        print(f"  • casos de avaliação: {len(data.get('eval_cases', []))}")
        
        valid_cases = 0
        missing_fields = []
        
        for case in data.get('eval_cases', []):
            has_all_fields = True
            required_fields = ['eval_id', 'conversation', 'session_input']
            
            for field in required_fields:
                if field not in case:
                    has_all_fields = False
                    missing_fields.append(f"Caso {case.get('eval_id', 'unknown')}: faltando {field}")
            
            if has_all_fields:
                if case['conversation'] and len(case['conversation']) > 0:
                    conv = case['conversation'][0]
                    if 'user_content' in conv and 'final_response' in conv:
                        valid_cases += 1
        
        print(f"  • casos válidos: {valid_cases}/{len(data.get('eval_cases', []))}")
        
        if missing_fields:
            print("\n  Problemas encontrados:")
            for msg in missing_fields[:5]:
                print(f"    - {msg}")
            if len(missing_fields) > 5:
                print(f"    ... e mais {len(missing_fields) - 5} problemas")
        
        if valid_cases == len(data.get('eval_cases', [])):
            print("\nArquivo válido!")
            return True
        else:
            print("\nArquivo gerado mas com problemas de validação")
            return False
        
    except json.JSONDecodeError:
        print(f"Erro: '{output_file}' não é um JSON válido")
        return False
    except Exception as e:
        print(f"Erro de validação: {e}")
        return False


def main():
    """Função principal com parsing de argumentos."""
    parser = argparse.ArgumentParser(
        description='Concatena arquivos de teste em um único benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s                                           # Usa valores padrão
  %(prog)s tests/custom output.json                 # Especifica entrada e saída
  %(prog)s --validate benchmark.json                # Apenas valida
  %(prog)s tests/dir --output final.json            # Usa flag --output
        """
    )
    
    parser.add_argument(
        'input_dir',
        nargs='?',
        default='tests/final_response',
        help='Diretório com arquivos de teste (padrão: tests/final_response)'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        default='agents/cemig_agent/teste_benchmark_complete.evalset.json',
        help='Arquivo de saída (padrão: teste_benchmark_complete.evalset.json)'
    )
    
    parser.add_argument(
        '--validate',
        metavar='FILE',
        help='Apenas valida o arquivo especificado'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Arquivo de saída alternativo (sobrescreve o argumento posicional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose com mais detalhes'
    )
    
    args = parser.parse_args()
    
    if args.validate:
        print("=" * 50)
        print("Modo: Validação")
        print("=" * 50)
        print("")
        success = validate_output(args.validate)
        sys.exit(0 if success else 1)
    
    output_file = args.output if args.output else args.output_file
    
    print("=" * 50)
    print("Concatenador de Testes - Benchmark")
    print("=" * 50)
    print(f"Entrada:  {args.input_dir}")
    print(f"Saída:    {output_file}")
    print("=" * 50)
    print("")

    success = concatenate_test_files(args.input_dir, output_file)
    
    if success:
        print("")
        print("=" * 50)
        print("Validando arquivo gerado...")
        print("=" * 50)
        print("")
        
        if validate_output(output_file):
            print("")
            print("Processo concluído com sucesso!")
            sys.exit(0)
        else:
            print("")
            print("Arquivo gerado mas com problemas de validação")
            sys.exit(1)
    else:
        print("")
        print("Processo falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()