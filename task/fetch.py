import asyncio
from itertools import islice
from traceback import print_exception
from linked_in.job_search import JobScraper, JobPage
from linked_in.authenticator import Authenticator
from model.job import Job
from task import Task
from page.util import browser

import zmq
from zmq.asyncio import Context

zctx = Context.instance()


class IndexJobs(Task):
    def __init__(self, ctx, port='5556') -> None:
        super().__init__(ctx)

        self.s = zctx.socket(zmq.PUSH)
        self.s.bind('tcp://127.0.0.1:%s' % port)

    async def execute(self):
        try: 
            with browser(headless=True) as driver:
                authenticator = Authenticator(driver, self.config)
                authenticator.start()
                
                for job_ids in islice(JobScraper(driver, self.config), 2): # only scrape the first 5 pages
                    print(job_ids)
                    await self.db.job.create_many(
                        data=[{"external_id": job_id} for job_id in job_ids],
                        skip_duplicates=True,
                    )

                    for job in job_ids:
                        self.s.send_string(job)

                print('finished index')
                        
        except asyncio.CancelledError as e:
            print('cancelling index')
            raise e

        finally:
            self.s.close()


    def execute_sync(self):
        asyncio.run(self.execute())

        


class FetchJobs(Task):

    def __init__(self, ctx, port='5556') -> None:
        super().__init__(ctx)

        self.s = zctx.socket(zmq.PULL)
        self.s.connect('tcp://127.0.0.1:%s' % port)
        
    async def execute(self):        
        try:
            with browser(headless=True) as driver:
                authenticator = Authenticator(driver, self.config)
                authenticator.start()
                
                while True:
                    print('waiting for fetch job')
                    job_id = await self.s.recv_string()
                    
                    try:
                        print(f'processing {job_id}')
                        data = JobPage.extract(driver, job_id)
                        job = await Job.upsert(job_id, data)
                        await job.summarize()

                    except ConnectionRefusedError as e:
                        print('browser has closed', e)
                    except Exception as e:
                        print('failed to extract', job_id, e)
                        print_exception(e)
                        raise e
                    finally:
                        print('processed', job_id)
        
        except asyncio.CancelledError as e:
            print('cancelling fetch')
            raise e

        finally: 
            self.s.close()


    def execute_sync(self):
        asyncio.run(self.execute())

