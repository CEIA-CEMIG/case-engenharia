import pytest
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "agents"))

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
        "markers", 
        "slow: marca testes que demoram para executar"
    )
    config.addinivalue_line(
        "markers", 
        "agent: testes relacionados ao agente CEMIG"
    )
    config.addinivalue_line(
        "markers", 
        "batch: testes executados em lote"
    )

def pytest_collection_modifyitems(config, items):
    """Modifica a coleta de itens de teste."""
    for item in items:

        if "agent" in item.name:
            item.add_marker(pytest.mark.agent)
        
        if "batch" in item.name:
            item.add_marker(pytest.mark.batch)
            item.add_marker(pytest.mark.slow)

@pytest.fixture(scope="session")
def project_root():
    """Fixture que retorna o diretório raiz do projeto."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture que retorna o diretório de dados de teste."""
    return Path(__file__).parent / "final_response"

@pytest.fixture
def agent_module_path():
    """Fixture que retorna o caminho do módulo do agente."""
    return "agents.cemig_agent.agent"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuração automática do ambiente de teste."""
    test_dir = Path(__file__).parent / "final_response"
    test_dir.mkdir(exist_ok=True)
    
    os.environ.setdefault("PYTEST_RUNNING", "1")
    
    yield
    pass

def pytest_runtest_setup(item):
    """Executado antes de cada teste."""
    if hasattr(item, 'callspec') and 'test_file' in item.callspec.params:
        test_file = item.callspec.params['test_file']
        print(f"\nPreparando teste: {os.path.basename(test_file)}")

def pytest_runtest_teardown(item):
    """Executado após cada teste."""
    pass

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Sumário customizado no final da execução."""
    if hasattr(terminalreporter, 'stats'):
        passed = len(terminalreporter.stats.get('passed', []))
        failed = len(terminalreporter.stats.get('failed', []))
        errors = len(terminalreporter.stats.get('error', []))
        skipped = len(terminalreporter.stats.get('skipped', []))
        
        total = passed + failed + errors + skipped
        
        print(f"\n{'='*60}")
        print(f"RESUMO FINAL - CEMIG Agent Tests")
        print(f"{'='*60}")
        print(f"Passou: {passed}")
        print(f"Falhou: {failed}")
        print(f"Erros: {errors}")
        print(f"Pulou: {skipped}")
        print(f"Total: {total}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"Taxa de sucesso: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("Excelente!")
            elif success_rate >= 60:
                print("Bom resultado!")
            else:
                print("Precisa de atenção...")

pytest_plugins = ["pytest_asyncio"]