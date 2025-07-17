from src.agents.prompts.utils.load_prompt import load_prompt
from src.agents.tools.get_schema_db import get_schema_db
from src.agents.tools.execute_sql_query import execute_sql_query
from src.agents.tools.get_schema_dictionary import get_schema_dictionary
from google.adk.agents import Agent

PROMPT_AGENT_ENGINEER = load_prompt("prompt_agent_engineer.txt")

root_agent = Agent(
    name="cemig_agent",
    model="gemini-2.0-flash",
    description=(
        "Agente especializado em questões da ANEEL com suporte a ferramentas."
    ),
    instruction=PROMPT_AGENT_ENGINEER,
    tools=[get_schema_db, execute_sql_query, get_schema_dictionary],
)