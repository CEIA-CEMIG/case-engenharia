import json
import csv
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class FinalResponseTestGenerator:
    """Gerador de arquivos de teste que avalia APENAS a resposta final do agente."""
    
    def __init__(self, agent_name: str = "cemig_agent"):
        self.agent_name = agent_name
        self.test_files_created = []
        
    def create_minimal_test_file(
        self,
        row: Dict[str, str],
        test_number: int,
        output_dir: str = "tests/final_response"
    ) -> str:
        """Cria um arquivo de teste minimalista focado apenas na resposta final."""

        test_structure = {
            "eval_set_id": f"final_response_test_{test_number:03d}",
            "name": f"Final Response Test #{test_number:03d}",
            "description": f"Avalia apenas a resposta final para: {row['query_lang']}...",
            "eval_cases": [
                {
                    "eval_id": f"case_{test_number:03d}",
                    "conversation": [
                        {
                            "invocation_id": str(uuid.uuid4()),
                            "user_content": {
                                "parts": [
                                    {
                                        "text": row['query_lang']
                                    }
                                ],
                                "role": "user"
                            },
                            "final_response": {
                                "parts": [
                                    {
                                        "text": self._format_expected_response(row)
                                    }
                                ],
                                "role": "model"
                            },
                            "intermediate_data": {
                                "tool_uses": [], 
                                "intermediate_responses": [] 
                            }
                        }
                    ],
                    "session_input": {
                        "app_name": self.agent_name,
                        "user_id": "test_user",
                        "state": {
                            "table_name": row['table_name'],
                            "evaluation_mode": "final_response_only"
                        }
                    }
                }
            ]
        }

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        filename = f"response_test_{test_number:03d}.test.json"
        filepath = Path(output_dir) / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_structure, f, indent=2, ensure_ascii=False)
        
        self.test_files_created.append(str(filepath))
        return str(filepath)
    
    def _format_expected_response(self, row: Dict[str, str]) -> str:
        """Formata a resposta esperada de forma flexível."""
        try:
            result = json.loads(row['result_expected'])
            
            if isinstance(result, list):
                total_records = len(result)
                preview_records = result 
            
            response = f"""Com base na sua solicitação, executei a análise na tabela {row['table_name']}.

                        Aqui estão os principais resultados:
                        {json.dumps(preview_records, indent=2, ensure_ascii=False)}

                        A consulta foi processada com sucesso e os dados foram organizados conforme solicitado."""
            
            return response
            
        except json.JSONDecodeError:
            return f"Resultado da consulta: {row['result_expected']}"
    
    def create_response_only_config(self, output_dir: str) -> str:
        """Cria configuração específica para avaliar apenas respostas finais."""
        
        config = {
            "criteria": {
                "tool_trajectory_avg_score": 0.0,  
                "response_match_score": 0.5  
            },
        }
        
        config_path = Path(output_dir) / "test_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return str(config_path)
    
    def generate_all_response_tests(
        self,
        csv_file: str,
        output_dir: str = "tests/final_response",
        sample_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Gera todos os testes focados em resposta final."""
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        error_count = 0
        errors = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader, 1):
                if sample_size and idx > sample_size:
                    break
                
                try:
                    filepath = self.create_minimal_test_file(row, idx, output_dir)
                    print(f"[{idx:03d}] Teste criado: {Path(filepath).name}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"[{idx:03d}] Erro: {str(e)[:50]}...")
                    error_count += 1
                    errors.append({
                        "row": idx,
                        "error": str(e)
                    })
        
        config_path = self.create_response_only_config(output_dir)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "FINAL_RESPONSE_ONLY",
            "total_tests_created": success_count,
            "errors": error_count,
            "error_details": errors[:10],  
            "output_directory": output_dir,
            "config_file": config_path,
            "note": "Estes testes avaliam APENAS a resposta final, ignorando ferramentas e passos intermediários"
        }
        
        report_path = Path(output_dir) / "generation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("RESUMO DA GERAÇÃO (Modo: Resposta Final)")
        print("="*60)
        print(f"Testes criados: {success_count}")
        print(f"Erros: {error_count}")
        print(f"Diretório: {output_dir}")
        print(f"Configuração: {config_path}")
        print(f"Relatório: {report_path}")
        
        return report


def main():
    """Script principal para gerar e executar testes de resposta final."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Gera testes ADK focados apenas em respostas finais'
    )
    parser.add_argument('action', choices=['generate', 'test', 'both'],
                       help='Ação a executar')
    parser.add_argument('csv_file', nargs='?',
                       help='Arquivo CSV (necessário para generate/both)')
    parser.add_argument('--output-dir', default='tests/final_response',
                       help='Diretório de saída')
    parser.add_argument('--sample', type=int,
                       help='Número de amostras para teste')
    parser.add_argument('--agent', default='cemig_agent',
                       help='Nome do módulo do agente')
    
    args = parser.parse_args()
    
    if args.action in ['generate', 'both']:
        if not args.csv_file:
            print("Erro: CSV file é necessário para gerar testes")
            return
        
        generator = FinalResponseTestGenerator(agent_name=args.agent)
        generator.generate_all_response_tests(
            csv_file=args.csv_file,
            output_dir=args.output_dir,
            sample_size=args.sample
        )
    
    if args.action in ['test', 'both']:
        import subprocess
        print("\nExecutando testes de resposta final...")
        cmd = f"pytest {__file__}::TestFinalResponseOnly -v"
        subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()