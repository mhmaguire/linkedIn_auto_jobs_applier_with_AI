import asyncio
from multiprocessing import Process
import textwrap

import click
from dotenv import load_dotenv

load_dotenv()
# ruff:noqa
from auto_resume.linked_in.linked_in import LinkedIn
from auto_resume.model.context import app
from auto_resume.task import FetchJobs, IndexJobs, Task
# ruff: enable


async def run(cmd: Task, site, *args):
    with app() as ctx:
        await cmd(site(), *args, ctx=ctx).execute()


def runner(task, site):
    try:
        asyncio.get_running_loop()
        asyncio.create_task(run(task, site))
    except RuntimeError as e:
        print(e)
        asyncio.run(run(task, site))


@click.group()
def main():
    pass


@main.command()
def fetch():
    Process(target=runner, args=(IndexJobs, LinkedIn)).start()
    for _ in range(3):
        Process(target=runner, args=(FetchJobs, LinkedIn)).start()


@main.command()
def serve():
    from auto_resume import app, socketio

    socketio.run(app, debug=True, port=3000)


@main.command()
def repl():
    import IPython
    from dotenv import load_dotenv

    load_dotenv()
    
    from traitlets.config import get_config
    from langchain_community.graphs import Neo4jGraph
    from auto_resume.linked_in.linked_in import LinkedIn
    from auto_resume.model.context import app
    

    with app() as ctx:

        
        c = get_config()
        c.InteractiveShellEmbed.colors = "Linux"
        
        
        IPython.embed(
            config=c,
            header=textwrap.dedent("""
            # Welcome to the Auto Resume REPL!
            #
            # You have access to the following variables:
            #   - ctx: The application context, which includes:
            #       - ctx.config: The loaded configuration
            #       - ctx.db: The Prisma database client
            #       - ctx.model: The Auto Resume model module
            #       - ctx.driver: The Selenium WebDriver instance
            #           - call ctx.browser() to initialize
            #   - Neo4jGraph: The Neo4j graph database client
            #   - LinkedIn: The LinkedIn scraper class
            #
            # Feel free to explore and interact with the application components!
            """)
        )


if __name__ == "__main__":
    main()
