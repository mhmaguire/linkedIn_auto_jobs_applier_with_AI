import asyncio
import re
import os
from itertools import islice
from traceback import print_exception
from pathlib import Path
import yaml
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import click

from pydantic import ValidationError


from agent.gpt import GPTAnswerer
from linked_in.authenticator import Authenticator

from linked_in.job_search import JobScraper, JobPage
from model.resume import Resume
from model.config import Config, Files

from prisma import Prisma


def ensure_chrome_profile():
    profile_dir = os.path.dirname(chromeProfilePath)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    if not os.path.exists(chromeProfilePath):
        os.makedirs(chromeProfilePath)
    return chromeProfilePath


chromeProfilePath = Path(Path.cwd(), "chrome_profile", "linkedin_profile")

def chromeBrowserOptions(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument("--auto-open-devtools-for-tabs");
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    ensure_chrome_profile()

    if chromeProfilePath:
        initialPath = chromeProfilePath.parent
        profileDir = chromeProfilePath.name
        print(str(initialPath), str(profileDir))
        options.add_argument('--user-data-dir=' + str(initialPath))
        options.add_argument("--profile-directory=" + str(profileDir))
    else:
        options.add_argument("--incognito")
        
    return options


def init_browser():
    try:
        options = chromeBrowserOptions()
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize browser: {str(e)}")
        print_exception(e)


class Bot:
    @classmethod
    def configure(cls, config, resume, db):
        driver = init_browser()

        return cls(driver=driver, config=config, resume=resume, db=db)

    def __init__(self, *, driver, config, resume, db):
        self.config = config
        self.resume = resume
        self.driver = driver
        self.db = db
        self.authenticator = Authenticator(driver)

        # self.gpt = GPTAnswerer(config.secrets.openai_api_key)

        self.scraper = JobScraper(driver, config)

        # self.gpt.set_resume(resume)
        self.authenticator.set_secrets(config.secrets.email, config.secrets.password)

        # self.manager.set_parameters(config.parameters.model_dump(by_alias=True))
        # self.manager.set_gpt_answerer(self.gpt)

        self.state = {}

    @property
    def email(self):
        return self.config.secrets.email

    @property
    def password(self):
        return self.config.secrets.password

    async def index_jobs(self):
        for job_ids in self.scraper:
            print(job_ids)
            await self.db.job.create_many(
                data=[{"external_id": job_id} for job_id in job_ids],
                skip_duplicates=True,
            )

    async def fetch_jobs(self):
        print(await self.db.job.count())

        jobs = await self.db.job.find_many()

        for job in islice(jobs, 100):

            try: 
                data = JobPage.extract(self.driver, job.external_id)

                poster = data.get("poster")
                company = data.get("company")
                payload = {
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "link": data.get("link"),
                }

                if company:
                    payload["company"] = {
                        "connectOrCreate": {
                            "where": {"link": company.get("link")},
                            "create": company,
                        }
                    }

                if poster:
                    payload["poster"] = {
                        "connectOrCreate": {
                            "where": {"link": poster.get("link")},
                            "create": poster,
                        }
                    }

                await self.db.job.update(
                    data=payload, where={"external_id": job.external_id}
                )

            except Exception as e:
                print_exception(e)
                print('failed to extract', job.external_id)

    async def start_login(self):
        self.authenticator.set_secrets(self.email, self.password)
        self.authenticator.start()
        self.state["logged_in"] = True

    def start_apply(self):
        self.apply_component.start_applying()


async def run(resume_path):
    try:
        Files.init()
        config = Config.load()
        resume = Resume.load(Files.plain_text_resume_file)
        db = Prisma()
        await db.connect()

        try:
            bot = Bot.configure(config, resume, db)
            await bot.start_login()
            # await bot.index_jobs()
            await bot.fetch_jobs()
            # bot.start_apply()
        except Exception as e:
            raise RuntimeError(f"Error running the bot: {str(e)}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print_exception(e)
    finally:
        await db.disconnect()


@click.command()
@click.option(
    "--resume",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="Path to the resume PDF file",
)
def main(resume: Path = None):
    asyncio.run(run(resume))


if __name__ == "__main__":
    main()
