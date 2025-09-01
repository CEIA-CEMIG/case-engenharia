import pytest
import os
from glob import glob
from google.adk.evaluation.agent_evaluator import AgentEvaluator

TEST_DIR = "tests/final_response"

def get_test_files(all_files_flag):
    """Retorna arquivos de teste baseado na flag."""
    if all_files_flag is False: 
        first_file = os.path.join(TEST_DIR, "response_test_001.test.json")
        if os.path.exists(first_file):
            return [first_file]
        else:
            available_files = glob(os.path.join(TEST_DIR, "*.test.json"))
            return available_files[:1] if available_files else []
    else:  
        return sorted(glob(os.path.join(TEST_DIR, "*.test.json")))

def pytest_generate_tests(metafunc):
    """Gera testes parametrizados dinamicamente."""
    if "test_file" in metafunc.fixturenames:
        all_files_flag = metafunc.config.getoption("--all-files", default=True)
        
        test_files = get_test_files(all_files_flag)
        
        if not test_files:
            pytest.skip(f"Nenhum arquivo de teste encontrado em {TEST_DIR}")
        
        test_ids = [os.path.basename(f).replace('.test.json', '') for f in test_files]
        
        metafunc.parametrize("test_file", test_files, ids=test_ids)

@pytest.mark.asyncio
async def test_agent_with_file(test_file):
    """Executa testes com base nos arquivos JSON encontrados."""
    print(f"\nExecutando: {os.path.basename(test_file)}")
    
    if not os.path.exists(test_file):
        pytest.fail(f"Arquivo de teste não encontrado: {test_file}")
    
    try:
        await AgentEvaluator.evaluate(
            agent_module="agents.cemig_agent.agent",
            eval_dataset_file_path_or_dir=test_file,
        )
        print(f"Sucesso: {os.path.basename(test_file)}")
        
    except Exception as e:
        print(f"Falha: {os.path.basename(test_file)}")
        print(f"Erro: {str(e)}")
        raise

@pytest.mark.asyncio 
async def test_agent_batch_all_files():
    """Executa todos os testes de uma vez (alternativa ao parametrizado)."""
    test_files = sorted(glob(os.path.join(TEST_DIR, "*.test.json")))
    
    if not test_files:
        pytest.skip(f"Nenhum arquivo de teste encontrado em {TEST_DIR}")
    
    print(f"\nExecutando {len(test_files)} testes em batch...")
    
    results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    for test_file in test_files:
        try:
            print(f"{os.path.basename(test_file)}")
            await AgentEvaluator.evaluate(
                agent_module="agents.cemig_agent.agent",
                eval_dataset_file_path_or_dir=test_file,
            )
            results["passed"] += 1
            print(f"Passou")
            
        except Exception as e:
            results["failed"] += 1
            error_msg = f"{os.path.basename(test_file)}: {str(e)}"
            results["errors"].append(error_msg)
            print(f"Falhou: {str(e)}")
    
    import json
    report_file = os.path.join(TEST_DIR, "test_execution_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultado Final:")
    print(f"Passou: {results['passed']}")
    print(f"Falhou: {results['failed']}")
    print(f"Relatório: {report_file}")
    
    total = results["passed"] + results["failed"]
    success_rate = results["passed"] / total if total > 0 else 0
    
    assert success_rate >= 0.7, f"Taxa de sucesso muito baixa: {success_rate:.1%} ({results['passed']}/{total})"

def pytest_addoption(parser):
    """Adiciona opções customizadas ao pytest."""
    parser.addoption(
        "--single-file", 
        action="store_false", 
        dest="all_files",
        default=True,
        help="Executa apenas o primeiro arquivo de teste (para debugging)"
    )
    parser.addoption(
        "--all-files", 
        action="store_true", 
        dest="all_files",
        default=True,
        help="Executa todos os arquivos de teste (padrão)"
    )

def pytest_configure(config):
    """Configuração adicional do pytest."""
    config.addinivalue_line(
        "markers", "slow: marca testes que demoram para executar"
    )

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "--all-files"]))