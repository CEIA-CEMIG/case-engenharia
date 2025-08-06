"""
Agente principal para questões da ANEEL.
"""
from .prompts.utils.load_prompt import load_prompt
from .prompts.utils.set_date_in_prompt import set_atual_date_in_prompt
from .tools.get_schema_db import get_schema_db
from .tools.execute_sql_query import execute_sql_query
from .tools.get_schema_dictionary import get_schema_dictionary
from google.adk.agents import Agent

prompt_loaded = load_prompt("prompt_agent_engineer.txt")
PROMPT_AGENT_ENGINEER = set_atual_date_in_prompt(prompt_loaded)

agent = Agent(
    name="cemig_agent",
    model="gemini-2.0-flash",
    description="Agente especializado em questões da ANEEL com suporte a ferramentas.",
    instruction=PROMPT_AGENT_ENGINEER,
    tools=[get_schema_db, execute_sql_query, get_schema_dictionary],
)

root_agent = agent