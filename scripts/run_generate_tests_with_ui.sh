#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="agents/cemig_agent/evals/utils/generate_benchmark_ui.py"
DEFAULT_INPUT="tests/final_response"
DEFAULT_OUTPUT="agents/cemig_agent/teste_benchmark_complete.evalset.json"

cd "$BASE_DIR"

show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   Concatenador de Benchmarks${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Uso: $0 [comando] [opções]"
    echo ""
    echo "Comandos:"
    echo "  concat [input] [output]  - Concatena arquivos de teste"
    echo "  validate [arquivo]        - Valida arquivo de benchmark"
    echo "  help                      - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 concat                                    # Usa padrões"
    echo "  $0 concat tests/custom output.json           # Custom"
    echo "  $0 validate teste_benchmark.json             # Validar"
    echo ""
}

COMMAND="${1:-concat}"

case "$COMMAND" in
    concat|concatenate)
        INPUT_DIR="${2:-$DEFAULT_INPUT}"
        OUTPUT_FILE="$DEFAULT_OUTPUT"
        
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}   Concatenando Arquivos de Teste${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${YELLOW}Entrada:${NC}  $INPUT_DIR"
        echo -e "${YELLOW}Saída:${NC}    $OUTPUT_FILE"
        echo ""
        
        if [ ! -d "$INPUT_DIR" ]; then
            echo -e "${RED}Diretório não existe: $INPUT_DIR${NC}"
            echo ""
            echo "Criando diretório..."
            mkdir -p "$INPUT_DIR"
            echo -e "${YELLOW}Execute primeiro: scripts/run_tests.sh generate${NC}"
            exit 1
        fi
        
        COUNT=$(ls -1 "$INPUT_DIR"/response_test_*.json 2>/dev/null | wc -l)
        if [ "$COUNT" -eq 0 ]; then
            echo -e "${RED}Nenhum arquivo de teste encontrado${NC}"
            echo ""
            echo -e "${YELLOW}Execute primeiro: scripts/run_tests.sh generate${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}Encontrados $COUNT arquivos para concatenar${NC}"
        echo ""
        
        python "$SCRIPT_PATH" "$INPUT_DIR" "$OUTPUT_FILE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}Concatenação concluída!${NC}"
            echo -e "  Arquivo: ${YELLOW}$OUTPUT_FILE${NC}"
        else
            echo -e "${RED}Erro na concatenação${NC}"
            exit 1
        fi
        ;;
        
    validate|val)
        FILE_TO_VALIDATE="${2:-$DEFAULT_OUTPUT}"
        
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}   Validando Arquivo de Benchmark${NC}"
        echo -e "${BLUE}========================================${NC}"
        echo ""
        
        python "$SCRIPT_PATH" --validate "$FILE_TO_VALIDATE"
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        echo -e "${RED}Comando desconhecido: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac