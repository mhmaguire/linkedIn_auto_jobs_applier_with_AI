from multiprocessing import Process
import asyncio
import click
from flask.cli import FlaskGroup

from auto_resume.task import Task, FetchJobs, IndexJobs
from auto_resume.model.context import app


async def run(cmd: Task):
    async with app() as ctx:
        await cmd(ctx).execute()


def runner(task):
    try:
        asyncio.get_running_loop()
        asyncio.create_task(run(task))
    except RuntimeError as e:
        print(e)
        asyncio.run(run(task))


@click.group()
def main():
    pass


@main.command()
def fetch():
    print("fetch")

    Process(target=runner, args=(IndexJobs,)).start()
    for _ in range(3):
        Process(target=runner, args=(FetchJobs,)).start()


@main.command()
def summary():
    print("summary")


if __name__ == "__main__":
    main()
