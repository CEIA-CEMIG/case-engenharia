"""
Utilitário para carregar arquivos de prompt.
"""
import os
from pathlib import Path

def load_prompt(filename):
    """Carrega um arquivo de prompt do diretório prompts"""
    current_dir = Path(__file__).parent.parent.parent  
    prompt_path = current_dir / "prompts" / filename
    
    alternative_paths = [
        prompt_path, 
        Path(__file__).parent.parent / filename, 
        Path(__file__).parent / filename,  
        Path.cwd() / "prompts" / filename, 
    ]
    
    for path in alternative_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
    
    raise FileNotFoundError(
        f"Arquivo de prompt '{filename}' não encontrado nos seguintes locais:\n" +
        "\n".join(f"  - {path}" for path in alternative_paths)
    )
