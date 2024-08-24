from multiprocessing import Process
import asyncio
import click
from auto_resume.linked_in.linked_in import LinkedIn

from auto_resume.task import Task, FetchJobs, IndexJobs
from auto_resume.model.context import app


async def run(cmd: Task, site, *args):
    async with app() as ctx:
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
    print("fetch")

    Process(target=runner, args=(IndexJobs, LinkedIn)).start()
    for _ in range(3):
        Process(target=runner, args=(FetchJobs, LinkedIn)).start()


@main.command()
def serve():
    from auto_resume import app, socketio

    socketio.run(app, debug=True)


if __name__ == "__main__":
    main()
