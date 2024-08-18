from multiprocessing import Process
import asyncio
import click

from task import Task, FetchJobs, IndexJobs
from model.context import app


async def run(cmd: Task):
    async with app() as ctx:
        await cmd(ctx).execute()


@click.group()
def main():
    pass


@main.command()
def fetch():
    print("fetch")

    def runner(task):
        asyncio.run(run(task()))

    Process(target=runner, args=(IndexJobs,)).start()
    Process(target=runner, args=(FetchJobs,)).start()


@main.command()
def summary():
    print("summary")


if __name__ == "__main__":
    main()
