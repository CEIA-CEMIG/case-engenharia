#!/bin/bash

SCRIPT_PATH="agents/cemig_agent/evals/utils/execute_query_for_benchmark.py"
INPUT_CSV="agents/cemig_agent/evals/data_for_benchmark/queries.csv"
OUTPUT_CSV="agents/cemig_agent/evals/data_for_benchmark/queries_with_results.csv"

echo "Gerando dados de teste..."
echo "Input: $INPUT_CSV"
echo "Output: $OUTPUT_CSV"
echo "----------------------------------------"

if [ "$1" == "--preview" ]; then
    python $SCRIPT_PATH $INPUT_CSV $OUTPUT_CSV --preview ${2:-10}
else
    python $SCRIPT_PATH $INPUT_CSV $OUTPUT_CSV
fi

echo "----------------------------------------"
echo "Processo concluído!"