#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")/.."

generate_tests() {
    echo -e "${BLUE}Gerando arquivos de teste...${NC}"
    
    python agents/cemig_agent/evals/utils/final_response_evaluator_with_pytest.py.py generate \
        agents/cemig_agent/evals/data_for_benchmark/queries_with_results.csv \
        --output-dir tests/final_response \
        $1
    
    if [ $? -eq 0 ]; then
        COUNT=$(ls -1 tests/final_response/*.test.json 2>/dev/null | wc -l)
        echo -e "${GREEN} $COUNT arquivos de teste gerados${NC}"
    else
        echo -e "${RED} Erro ao gerar testes${NC}"
        exit 1
    fi
}

run_tests() {
    echo -e "${BLUE}Executando testes...${NC}"
    
    pytest tests/test_final_response.py -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN} Testes executados com sucesso${NC}"
    else
        echo -e "${YELLOW} Alguns testes falharam${NC}"
    fi
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Sistema de Testes - CEMIG Agent${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

case "${1:-help}" in
    generate)

        SAMPLE=""
        if [ "$2" = "--sample" ] && [ -n "$3" ]; then
            SAMPLE="--sample $3"
            echo -e "${YELLOW}Modo:${NC} Gerar testes (amostra de $3)"
        else
            echo -e "${YELLOW}Modo:${NC} Gerar todos os testes"
        fi
        echo ""
        generate_tests "$SAMPLE"
        ;;
        
    test)

        echo -e "${YELLOW}Modo:${NC} Executar testes"
        echo ""
        run_tests
        ;;
        
    both)

        SAMPLE=""
        if [ "$2" = "--sample" ] && [ -n "$3" ]; then
            SAMPLE="--sample $3"
            echo -e "${YELLOW}Modo:${NC} Gerar (amostra de $3) e executar"
        else
            echo -e "${YELLOW}Modo:${NC} Gerar todos e executar"
        fi
        echo ""
        generate_tests "$SAMPLE"
        echo ""
        run_tests
        ;;
        
    clean)

        echo -e "${YELLOW}Modo:${NC} Limpar arquivos de teste"
        echo ""
        if [ -d "tests/final_response" ]; then
            rm -f tests/final_response/*.test.json
            rm -f tests/final_response/*.json
            echo -e "${GREEN} Arquivos limpos${NC}"
        else
            echo -e "${YELLOW}Nada para limpar${NC}"
        fi
        ;;
        
    *)
        echo "Uso: $0 [comando] [opções]"
        echo ""
        echo "Comandos:"
        echo "  generate [--sample N]  - Gera arquivos de teste"
        echo "  test                   - Executa os testes"
        echo "  both [--sample N]      - Gera e executa"
        echo "  clean                  - Remove arquivos de teste"
        echo ""
        echo "Exemplos:"
        echo "  $0 generate            # Gera todos os testes"
        echo "  $0 generate --sample 5  # Gera 5 testes de amostra"
        echo "  $0 test                 # Executa testes existentes"
        echo "  $0 both --sample 10     # Gera 10 e executa"
        echo "  $0 clean                # Limpa arquivos gerados"
        ;;
esac

echo ""