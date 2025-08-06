from datetime import datetime

def set_atual_date_in_prompt(prompt: str) -> str:
    """
    Substitui a data atual no prompt por uma data formatada.
    
    Args:
        prompt (str): O prompt original que contém a data a ser substituída.
    
    Returns:
        str: O prompt com a data atual formatada.
    """
    current_date = datetime.now().strftime("%d/%m/%Y")
    return prompt.replace("{date}", current_date)