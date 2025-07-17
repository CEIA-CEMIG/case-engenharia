import asyncio
from google.adk.cli.cli import run_cli

if __name__ == "__main__":
    asyncio.run(
        run_cli(
            agent_parent_dir="src",
            agent_folder_name="agents",
            save_session=True,
        )
    )
