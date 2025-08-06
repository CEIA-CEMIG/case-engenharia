import pytest
import os
from glob import glob
from google.adk.evaluation.agent_evaluator import AgentEvaluator

TEST_DIR = "tests/final_response"

def get_test_files(all_files_flag):
    if all_files_flag:
        return glob(os.path.join(TEST_DIR, "*.test.json"))
    else:
        return [os.path.join(TEST_DIR, "response_test_001.test.json")]

def pytest_generate_tests(metafunc):
    if "test_file" in metafunc.fixturenames:
        all_files_flag = metafunc.config.getoption("all_files")
        test_files = get_test_files(all_files_flag)
        metafunc.parametrize("test_file", test_files)

@pytest.mark.asyncio
async def test_agent_with_file(test_file):
    """Executa testes com base nos arquivos JSON encontrados."""
    await AgentEvaluator.evaluate(
        agent_module="agents.cemig_agent.agent",
        eval_dataset_file_path_or_dir=test_file,
    )
