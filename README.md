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
# No terminal, digite
adk web
```
