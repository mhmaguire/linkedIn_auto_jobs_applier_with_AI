from auto_resume.linked_in.authenticator import Authenticator
from auto_resume.linked_in.job_search import JobPage, JobScraper, JobSearchPage
from auto_resume.model.config import Config
from auto_resume.page import Site


class LinkedIn(Site):
    def __init__(self) -> None:
        super().__init__()

        self.config = Config.load()
        self.scraper = JobScraper(self.config)
        self.authenticator = Authenticator(self.config)

    def search_page(self, driver):
        return JobSearchPage(driver).go()

    def job_page(self, driver, job_id):
        return JobPage(driver, job_id).go()

    def authenticate(self, driver):
        self.authenticator.start(driver)

    def search(self, driver):
        for x in self.scraper.start(driver):
            yield x

    def job(self, driver, job_id):
        return JobPage.extract(driver, job_id)
