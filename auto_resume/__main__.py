from multiprocessing import Process
import asyncio
import click

from auto_resume.task import Task, FetchJobs, IndexJobs
from auto_resume.model.context import app


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
        asyncio.run(run(task))

    Process(target=runner, args=(IndexJobs,)).start()
    for _ in range(3):
        Process(target=runner, args=(FetchJobs,)).start()


@main.command()
def summary():
    print("summary")


if __name__ == "__main__":
    main()
