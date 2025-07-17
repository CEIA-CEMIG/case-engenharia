from pathlib import Path

def load_prompt(nome_arquivo: str, diretorio: str = "src/agents/prompts") -> str:
    """Lê o conteúdo de um arquivo .txt e retorna como string."""
    caminho = Path(diretorio) / nome_arquivo
    
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    
    return caminho.read_text(encoding="utf-8")