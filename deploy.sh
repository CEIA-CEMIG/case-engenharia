#!/bin/bash

# Script de deploy para a aplicação CEMIG

# Configuração dos parâmetros
PROJECT="ufg-prd-energygpt"
REGION="us-central1"
SERVICE_NAME="case-engenharia"
APP_NAME="cemig-agent-app"
AGENT_PATH="agents/cemig_agent"

echo "Iniciando deploy da aplicação CEMIG..."

adk deploy cloud_run \
  --project="$PROJECT" \
  --region="$REGION" \
  --service_name="$SERVICE_NAME" \
  --app_name="$APP_NAME" \
  --with_ui \
  "$AGENT_PATH"

echo "Deploy concluído!"