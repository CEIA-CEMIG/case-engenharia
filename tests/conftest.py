def pytest_addoption(parser):
    parser.addoption(
        "--all-files",
        action="store_true",
        default=False,
        help="Executa todos os arquivos .test.json da pasta tests/final_response",
    )
