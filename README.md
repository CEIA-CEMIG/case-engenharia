# Case Engenharia 

Sistema **Text2SQL** para a área de Engenharia.

## Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
```

### 2. Configuração com Poetry (se quiser)

#### Instalar Poetry (se não tiver)

```bash
# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Configurar ambiente virtual e dependências

```bash
# Instalar dependências do projeto
poetry install

# Ativar ambiente virtual
poetry shell

# OU executar comandos diretamente
poetry run python main.py
```

#### Comandos úteis do Poetry

```bash
# Adicionar nova dependência
poetry add nome-da-biblioteca

# Adicionar dependência de desenvolvimento
poetry add --group dev nome-da-biblioteca

# Atualizar dependências
poetry update

# Ver dependências instaladas
poetry show

# Sair do ambiente virtual
exit
```
### 3. Configuração Google Cloud

#### Autenticação

```bash
# Login no Google Cloud
gcloud auth login

# Configurar projeto padrão
gcloud config set project ufg-prd-energygpt

# Verificar configuração
gcloud config list
```

### 4. Configuração do Banco de Dados

#### Conectar ao banco via túnel SSH

```bash
# Iniciar túnel para o banco PostgreSQL
gcloud compute start-iap-tunnel application-bastion-vm 5432 --local-host-port=localhost:5435 --zone=us-central1-a --project=ufg-prd-energygpt
```

**Importante**: Mantenha este terminal aberto enquanto usar o sistema.

#### Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5435
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DATABASE=case-engenharia
POSTGRES_DEFAULT_DB=postgres

# Google Cloud Configuration
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=ufg-prd-energygpt
GOOGLE_CLOUD_LOCATION=us-central1
```
-----

## Executando:

1. Interface do ADK:
```python
Em agents/ 
(~/case-engenharia/agents)

# No terminal, digite
adk web
```

## Deploy:

```python
1.
chmod +x deploy.sh

2.
./deploy.sh
```

## Testes:

### Geração do Benchmark:

- Atualmente, estamos utilizando 2 formas de avaliar o fluxo:
    1. Pytest
    2. UI (Própia do ADK Evals)

- Ambos os testes são funcionais porém, a forma de visualizar os resultados pela UI, precisa ser refinada para facilitar o entendimento (**In progress**)

### Como gerar os resultados da avaliação:

1. Partimos de um csv base contendo as informações básicas para gerar o benchmark. Inclua em 'querie.csv' as informações da nova tabela que deseja criar os testes.

- **table_name**: Nome da tabela no banco
- **query_sql**: Query real do banco (funcional)
- **query_lang**: Texto em linguagem natural que representa a query em questão

``` python
agents/cemig_agent/evals/data_for_benchmark/querie.csv
```
---
2. Após adicionar as queries, inicie uma conexão com o banco.

```python
# Iniciar túnel para o banco PostgreSQL
gcloud compute start-iap-tunnel application-bastion-vm 5432 --local-host-port=localhost:5435 --zone=us-central1-a --project=ufg-prd-energygpt
```
---
3. Execute o script *'run_generate_csv_with_responses.sh'* para rodar as consultas e armazenar os resultados da sua query.

    ```python
    chmod +x scripts/run_generate_csv_with_responses.sh

    # Rodar todas as queries
    ./scripts/run_generate_csv_with_responses.sh

    # Ou com preview de 10 queries
    ./scripts/run_generate_csv_with_responses.sh --preview 10
    ```

Ao fim, caso tudo dê certo, devemos ter queries_with_results.csv atualizado:

```python
├── cemig_agent
│   ├── evals
│   │   ├── data_for_benchmark
│   │   │   ├── queries.csv
│   │   │   └── queries_with_results.csv
```

---
4. A proxima etapa é gerar arquivos de teste a partir do CSV 'queries_with_results.csv'.

- Execute o script *'run_generate_tests.sh'* para gerar arquivos de teste que serão usados na avaliação via pytest.

- Os arquivos gerados ficarão armazenados em:

    ```python
    case-engenharia/tests/final_response
    ```

- Serão gerados 3 tipos de arquivos:
    -  **generation_report.json**: Com informações gerais dos testes.
    -  **response_test_*.test**: Com o teste a ser executado (seu respectivo número).
    - **test_config.json**: Com os criterios de aprovação por similaridade da resposta padrão com a esperada. (Threshold está em 0.5 - Estamos avaliando apenas pela resposta final *'response_match_score'*).

    ```python
    #Tornar executável
    chmod +x scripts/run_generate_tests.sh

    # Gerar todos os testes
    ./scripts/run_generate_tests.sh generate

    # Gerar apenas uma amostra (ex: 5 testes)
    ./scripts/run_generate_tests.sh generate --sample 5

    # Executar os testes existentes
    ./scripts/run_generate_tests.sh test

    # Gerar e executar todos os testes
    ./scripts/run_generate_tests.sh both

    # Gerar e executar apenas uma amostra
    ./scripts/run_generate_tests.sh both --sample 10

    # Limpar arquivos de teste gerados
    ./scripts/run_generate_tests.sh clean

    ```
---
5. Caso queira gerar os testes para executar na UI do ADK, realize as etapas anteriores e concatene os testes unitários gerados para uma estrutura aceita pelo ADK.

    ```python
    # Tornar o script executável
    chmod +x scripts/run_generate_tests_with_ui.sh

    # Concatenar arquivos de teste usando os padrões (input: tests/final_response, output: teste_benchmark_complete.evalset.json)
    ./scripts/run_generate_tests_with_ui.sh concat

    # Validar um arquivo de benchmark
    ./scripts/run_generate_tests_with_ui.sh validate

    # Mostrar ajuda e exemplos de uso
    ./scripts/run_generate_tests_with_ui.sh help
    ```
---
6. O arquivo gerado deve terminar em '.evalset.json' e estar no mesmo path de 'agent.py'
---
### Importante:

Para nosso agente funcionar corretamente, precisamos incluir em 'agents/cemig_agent/tools/utils/mapping_tables.yaml' a tabela adicionada e seu respectivo dicionário de dados. O dicionário deve estar em um bucket no gcp:

- BUCKET_NAME = "application-case-engenharia"
- PATH_PREFIX = "dicionario_de_dados/"


---
