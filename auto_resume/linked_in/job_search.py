import random
import time
from itertools import product
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from auto_resume.page.page import Page
from auto_resume.page.element import Element
from auto_resume.model.config import Config, ExperienceLevel, JobType, WorkType

from urllib.parse import urlencode, quote, urlparse

from pprint import pprint


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
    pagination = Element.one((By.CLASS_NAME, 'jobs-search-results-list__pagination'))

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
        page.wait_for(page.pagination.present())
        print('pagination visible')
        print('is scrolled', page.scrolled_bottom())

        while not page.scrolled_bottom():
            print('scrolling')
            page.scroll(results, 1000)
            time.sleep(random.uniform(1.0, 2.6))

        print('scrolled')
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

    title_el = Element.one((By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__job-title'))
    details = Element.many((By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__primary-description-container span'))
    highlights = Element.many((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-insight--highlight"))
    description_el = Element.one((By.CSS_SELECTOR, '#job-details'))
    more_description = Element.one((By.CSS_SELECTOR, '.jobs-description footer button'))
    salary = Element.one((By.CSS_SELECTOR, '#SALARY'))

    company_el = Element.one((By.CLASS_NAME, 'job-details-jobs-unified-top-card__company-name'))
    company_link_el = Element.one((By.CSS_SELECTOR, '.job-details-jobs-unified-top-card__company-name a'))
    company_description_el = Element.one((By.CSS_SELECTOR, '.jobs-company__company-description'))

    poster_el = Element.one((By.CSS_SELECTOR, 'a:has(+ .hirer-card__hirer-information)'))
    poster_name_el = Element.one((By.CSS_SELECTOR, '.hirer-card__hirer-information .jobs-poster__name strong'))
    

    def __init__(self, driver=None, job_id=None):
        super().__init__(driver)

        self.job_id = job_id

    def link(self):
        return job_url(self.job_id)

    def go(self):
        self.driver.get(self.link())


    @property
    def poster(self):
        
        poster = dict(link=self.poster_link, name=self.poster_name)

        if poster.get('name', False) and poster.get('link', False):
            return poster
        else:
            return None


    @property
    def poster_link(self):
        if el := self.poster_el():
            return el.get_attribute('href')

    @property
    def poster_name(self):    
        if el := self.poster_name_el():
            return el.text
    
    @property
    def company_link(self):
        if el := self.company_link_el():
            return el.get_attribute('href')

    @property
    def company(self):
        if el := self.company_el():
            return el.text 

    @property
    def company_description(self):
        if el := self.company_description_el():
            return el.text

    @property
    def title(self):
        if el := self.title_el():
            return el.text

    @property
    def description(self):
        if el := self.description_el():
            return el.text


    def data(self):

        self.expand_description()

        company = dict(name=self.company, link=self.company_link, description=self.company_description)

        pprint(company)
        
        return dict(
            title=self.title,
            # details=' '.join([el.text for el in self.details()]),
            # highlights=' '.join([el.text for el in self.highlights()]),
            description=self.description,
            company=company,
            poster=self.poster,
            link=self.link()
        )

    def expand_description(self):
        if el := self.more_description():
            el.click()

    @classmethod
    def extract(cls, driver, job_id):
        job = cls(driver, job_id)
        job.go()
        return job.data()        