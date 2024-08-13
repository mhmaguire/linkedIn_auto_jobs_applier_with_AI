import random
import time
from itertools import product
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

from page.page import Page
from page.element import Element
from model.config import Config, ExperienceLevel, JobType, WorkType

from urllib.parse import urlencode, quote, urlparse


def job_url(job_id):
    return f'https://linkedin.com/jobs/view/{job_id}'

def job_query(parameters):

    # distance=25 # distance
    # &f_E=2%2C3%2C4 # experience
    # &f_JT=F%2CC%2CT # JOB TYPE F P C T V I O
    # &f_TPR=r2592000 # DATE
    # &f_WT=1%2C2%2C3 # Work Type  
    # &f_AL=true  # easy apply 

    levels = [ExperienceLevel[level].param for level, value in parameters.experience_level if value]
    types = [JobType[t].param for t, value in parameters.job_types if value]
    work = [WorkType[t].param for t, value in parameters.work_types if value]
    date = parameters.date.param

    return dict(
        distance=parameters.distance,
        f_E=','.join(levels),
        f_JT=','.join(types),
        f_WT=','.join(work),
        f_TPR=date
    )


def job_search_url(parameters, position, location, page=0):
    qs = urlencode(dict(
        **job_query(parameters), 
        geoId=location,
        keywords=position,
        start=page * 25
    ), quote_via=quote)
    
    return f'https://linkedin.com/jobs/search/?{qs}'



class JobSearchPage(Page):
    url = 'https://www.linkedin.com/jobs/search'
    
    no_jobs_element = Element.one((By.CLASS_NAME, 'jobs-search-two-pane__no-results-banner--expand'))
    results = Element.one((By.CLASS_NAME, "jobs-search-results-list"))
    jobs = Element.many((By.CSS_SELECTOR, '[data-job-id]'))

    def __init__(self, driver):
        super().__init__(driver)


    def scrolled_bottom(self):
        results = self.results()
        height = int(results.get_property('scrollHeight'))
        top = int(results.get_property('scrollTop'))
        client = int(results.get_property('clientHeight'))

        return (height - top) <= client

    def scroll(self, el, scrollY):
        actions = ActionChains(self.driver)
        actions.move_to_element(el)
        actions.scroll_from_origin(ScrollOrigin.from_element(el), 0, scrollY)
        actions.perform()
        


class JobSearch():

    def __init__(self, driver, position, location, parameters):
        self.driver = driver
        self.position = position
        self.location = location
        self.parameters = parameters

    def __iter__(self):
        page = 0
        while True:
            url = job_search_url(
                self.parameters, 
                self.position, 
                self.location, 
                page
                )
            
            yield url
            
            page = page + 1 


class JobScraper(Page):
    def __init__(self, driver, config: Config):
        super().__init__(driver)
        self.config = config

    @property
    def locations(self):
        return self.config.parameters.locations

    @property
    def positions(self):
        return self.config.parameters.positions

    def process_search(self):
        page = JobSearchPage(self.driver)

        results = page.wait_for(page.results.visible())
        print('results visible')
        print('is scrolled', page.scrolled_bottom())

        while not page.scrolled_bottom():
            print('scrolling')
            page.scroll(results, 1000)
            time.sleep(random.uniform(1.0, 2.6))

        return [job.get_attribute('data-job-id') for job in page.jobs()]
                    

    def __iter__(self):
        for (position, location) in product(self.positions, self.locations):

            search = iter(JobSearch(self.driver, position, location, self.config.parameters))

            print('first')
            self.driver.get(next(search))

            yield self.process_search()

            while next_page := self.driver.find_element(By.CSS_SELECTOR, 'li:has(button[aria-current=true]) + li'):
                next_page.click()

                yield self.process_search()


        
class JobPage(Page):

    title = Element.one((By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-title'))
    details = Element.many((By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__primary-description-container span'))
    highlights = Element.many((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-insight--highlight"))
    description = Element.one((By.CSS_SELECTOR, '#job-details'))
    more_description = Element.one((By.CSS_SELECTOR, '.jobs-description footer button'))
    salary = Element.one((By.CSS_SELECTOR, '#SALARY'))

    company = Element.one((By.CSS_SELECTOR, 'a[href*="/company"]'))
    company_description = Element.one((By.CSS_SELECTOR, '.jobs-company__company-description'))

    poster = Element.one((By.CSS_SELECTOR, 'a:has(+ .hirer-card__hirer-information)'))
    poster_name = Element.one((By.CSS_SELECTOR, '.hirer-card__hirer-information .jobs-poster__name strong'))
    

    def __init__(self, driver=None, job_id=None):
        super().__init__(driver)

        self.job_id = job_id

    def link(self):
        return job_url(self.job_id)

    def go(self):
        self.driver.get(self.link())

    def data(self):

        self.more_description().click()

        try: 
            poster = dict(link=self.poster().get_attribute('href'), name=self.poster_name().text)
        except: 
            poster = None
        
        return dict(
            title=self.title().text,
            details=' '.join([el.text for el in self.details()]),
            highlights=' '.join([el.text for el in self.highlights()]),
            description=self.description().text,
            company=dict(name=self.company().text, link=self.company().get_attribute('href'), description=self.company_description().text),
            poster=poster,
            link=self.link()
        )

    @classmethod
    def extract(cls, driver, job_id):
        job = cls(driver, job_id)
        job.go()
        return job.data()        