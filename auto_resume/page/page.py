from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Page:
    def __init__(self, driver=None):
        self.driver = driver

    def await_url(self, url):
        self.wait_for(EC.url_contains(url))

    def await_presence(self, locator):
        return self.wait_for(EC.presence_of_element_located(locator))

    def await_pageload(self):
        self.wait_for(lambda d: d.execute_script('return document.readyState') == 'complete')

    def wait_for(self, condition, timeout=10):
        return WebDriverWait(self.driver, timeout).until(condition)