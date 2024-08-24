import asyncio
from itertools import islice
from traceback import print_exception
from auto_resume.model.job import Job
from auto_resume.task import Task
from auto_resume.page.util import browser

import zmq
from zmq.asyncio import Context
from auto_resume.model.context import AppContext

zctx = Context.instance()


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

        self.platform = platform

    async def execute(self) -> None:
        """
        Execute the IndexJobs task asynchronously. This method scrapes job IDs and stores them in the database.
        """
        try:
            with browser(headless=True) as driver:
                self.platform.authenticate(driver)

                for job_ids in islice(
                    self.platform.search(driver), 2
                ):  # only scrape the first 5 pages
                    print(job_ids)
                    self.db.job.create_many(
                        data=[{"external_id": job_id} for job_id in job_ids],
                        skip_duplicates=True,
                    )

                    for job in job_ids:
                        self.s.send_string(job)

                print("finished index")

        except asyncio.CancelledError as e:
            print("cancelling index")
            raise e

        finally:
            self.s.close()

    def execute_sync(self) -> None:
        """
        Execute the IndexJobs task synchronously.
        """
        asyncio.run(self.execute())


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
        self.platform = platform

    async def execute(self) -> None:
        """
        Execute the FetchJobs task asynchronously. This method fetches job details and processes them.
        """
        try:
            with browser(headless=True) as driver:
                self.platform.authenticate(driver)

                while True:
                    print("waiting for fetch job")
                    job_id = await self.s.recv_string()

                    try:
                        print(f"processing {job_id}")
                        data = self.platform.job(driver, job_id)
                        job = await Job.upsert(job_id, data)
                        await job.summarize()
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
