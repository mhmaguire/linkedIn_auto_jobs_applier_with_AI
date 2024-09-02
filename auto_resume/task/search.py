import asyncio
from itertools import islice
from traceback import print_exception
from pprint import pprint

from flask_socketio import SocketIO
from auto_resume.model.job import Job
from auto_resume.task.task import Task
from auto_resume.page.util import browser, init_browser
from auto_resume.linked_in.linked_in import LinkedIn

import zmq
from zmq.asyncio import Context
from auto_resume.model.context import AppContext, app
from threading import Thread

zctx = Context.instance()

import asyncio
from multiprocessing import Process

# ruff:noqa
# ruff: enable

def sock():
    return SocketIO(message_queue='redis://')

def search():
    async def run(cmd: Task, site, *args):
        print('RUN', cmd, site)
        with app() as ctx:
            print('APP CONTEXT', ctx)
            await cmd(site(), *args, ctx=ctx).execute()

    def runner(task, site):
        try:
            asyncio.get_running_loop()
            asyncio.create_task(run(task, site))
        except RuntimeError as e:
            pprint(e)
            asyncio.run(run(task, site))

    Process(target=runner, args=(IndexJobs, LinkedIn)).start()
    for _ in range(3):
        Process(target=runner, args=(FetchJobs, LinkedIn)).start()


class IndexJobs(Task):
    def __init__(self, platform, *, ctx: AppContext, port: str = "5556" ) -> None:
        """
        Initialize the IndexJobs task with the given application context and port.

        :param ctx: The application context containing configuration and database access.
        :param port: The port to bind the ZMQ PUSH socket to.
        """
        super().__init__(ctx)
        self.s = zctx.socket(zmq.PUSH)
        self.s.bind(f"tcp://127.0.0.1:{port}")
        self.sio = sock()
        self.ctx = ctx

        self.platform = platform

    async def execute(self) -> None:
        """
        Execute the IndexJobs task asynchronously. This method scrapes job IDs and stores them in the database.
        """
        try:
            with init_browser(headless=True) as driver:
                self.sio.emit('message', {'name': 'auth_start', 'data': {}}, namespace='/auto_resume')
                self.platform.authenticate(driver)

                self.sio.emit('message', {'name': 'index_start', 'data': {}}, namespace='/auto_resume')

                for job_ids in islice(
                    self.platform.search(driver), 2
                ):  # only scrape the first 5 pages
                    
                    self.db.job.create_many(
                        data=[{"external_id": job_id} for job_id in job_ids],
                        skip_duplicates=True,
                    )

                    for job in job_ids:
                        self.s.send_string(job)

                self.sio.emit('message', {'name': 'index_finish', 'data': {}}, namespace='/auto_resume')

        except asyncio.CancelledError as e:
            print("cancelling index")
            raise e

        finally:
            self.s.close()


class FetchJobs(Task):
    def __init__(self, platform, *, ctx: AppContext, port: str = "5556") -> None:
        """
        Initialize the FetchJobs task with the given application context and port.

        :param ctx: The application context containing configuration and database access.
        :param port: The port to connect the ZMQ PULL socket to.
        """
        super().__init__(ctx)
        self.s = zctx.socket(zmq.PULL)
        self.s.connect(f"tcp://127.0.0.1:{port}")
        self.sio = sock()
        self.platform = platform
        self.ctx = ctx

    async def execute(self) -> None:
        """
        Execute the FetchJobs task asynchronously. This method fetches job details and processes them.
        """
        try:
            with init_browser(headless=True) as driver:
                self.platform.authenticate(driver)

                while True:
                    print("waiting for fetch job")

                    job_id = await self.s.recv_string()

                    try:
                        print(f"processing {job_id}")

                        self.sio.emit('message', {'name': 'job_process', 'data': {'id': job_id}}, namespace='/auto_resume')

                        data = self.platform.job(driver, job_id)
                        job = Job.upsert(job_id, data)
                        self.sio.emit('message',
                            {'name': 'job_extract', 
                             'data': {'id': job_id}
                            },namespace='/auto_resume')
                        
                        await job.summarize()
                        self.sio.emit('message', {'name': 'job_summarize', 'data': {'id': job_id}}, namespace='/auto_resume')
                        
                        await job.index()

                    except ConnectionRefusedError as e:
                        print("browser has closed", e)
                    except Exception as e:
                        print("failed to extract", job_id, e)
                        print_exception(e)
                        raise e
                    finally:
                        print("processed", job_id)

        except asyncio.CancelledError as e:
            print("cancelling fetch")
            raise e

        finally:
            self.s.close()

    def execute_sync(self) -> None:
        """
        Execute the FetchJobs task synchronously.
        """
        asyncio.run(self.execute())
