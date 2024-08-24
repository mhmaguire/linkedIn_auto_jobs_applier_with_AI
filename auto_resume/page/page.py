from selenium import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from typing import Callable, TypeVar, Union
from selenium.webdriver.remote.webelement import WebElement


T = TypeVar('T')


class Page:
    def __init__(self, driver: WebDriver) -> None:
        """
        Initialize the Page object with a WebDriver instance.

        :param driver: WebDriver instance to interact with the web page.
        """
        self.driver = driver

    def await_url(self, url: str) -> None:
        """
        Wait until the URL contains the specified substring.

        :param url: Substring to be present in the URL.
        """
        self.wait_for(EC.url_contains(url))

    def await_presence(self, locator: tuple[By, str]) -> Union[WebElement, list[WebElement]]:
        """
        Wait until the presence of an element located by the given locator.

        :param locator: Locator tuple (By, value) to find the element.
        :return: The WebElement once it is located.
        """
        return self.wait_for(EC.presence_of_element_located(locator))

    def await_pageload(self) -> None:
        """
        Wait until the page has completely loaded.
        """
        self.wait_for(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for(self, condition: Callable[[WebDriver], T], timeout: int = 10) -> T:
        """
        Wait for a specific condition to be met within the given timeout.

        :param condition: A callable that takes a WebDriver instance and returns a value of type T.
        :param timeout: Maximum time to wait for the condition to be met.
        :return: The result of the condition callable.
        """
        return WebDriverWait(self.driver, timeout).until(condition)
