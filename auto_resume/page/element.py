import types
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Union, Callable, Type, Optional, Protocol, Tuple

class HasDriver(Protocol):
    driver: WebDriver

Locator = Tuple[By, str]

class Element:
    def __init__(self, locator: Locator, many: bool = True) -> None:
        """
        Initialize the Element object with a locator and a flag indicating if multiple elements are expected.

        :param locator: Locator tuple (By, value) to find the element(s).
        :param many: Boolean flag indicating if multiple elements are expected.
        """
        self.locator = locator
        self.is_many = many
        self.timeout = 1

    def __set_name__(self, owner: Type, name: str) -> None:
        """
        Set the name of the attribute on the owner class.

        :param owner: The owner class where the attribute is defined.
        :param name: The name of the attribute.
        """
        self.__name__ = name

    def __call__(self, instance: HasDriver, timeout: int = 10, reraise: bool = False) -> Union[bool, WebElement, list[WebElement]]:
        """
        Call the element, waiting for its presence and optionally raising exceptions.

        :param instance: The instance of the class where the element is defined.
        :param timeout: Maximum time to wait for the element.
        :param reraise: Boolean flag to indicate if exceptions should be re-raised.
        :return: The WebElement(s) if found, otherwise False.
        """
        try:
            return instance.wait_for(self.present(), timeout=timeout)
        except (NoSuchElementException, TimeoutException) as e:
            if reraise:
                raise e
            return False

    def __get__(self, instance: Optional[HasDriver], owner: Type) -> Union[Callable, Locator]:
        """
        Get the element, returning a method if accessed through an instance, or the locator if accessed through the class.
        Uses the descriptor protocol to lazily get the fresh driver from the host object.

        :param instance: The instance of the class where the element is defined.
        :param owner: The owner class where the attribute is defined.
        :return: A method bound to the instance or the locator tuple.
        """
        if instance is None:
            return self.locator
        return types.MethodType(self, instance)

    def find(self, driver: WebDriver) -> Union[WebElement, list[WebElement]]:
        """
        Find the element(s) using the provided WebDriver.

        :param driver: WebDriver instance to interact with the web page.
        :return: The WebElement(s) found by the locator.
        """
        if self.is_many:
            return driver.find_elements(*self.locator)
        else:
            return driver.find_element(*self.locator)

    def visible(self) -> Callable:
        """
        Get the expected condition for the visibility of the element(s).

        :return: The expected condition for visibility.
        """
        if self.is_many:
            return EC.visibility_of_all_elements_located(self.locator)
        else:
            return EC.visibility_of_element_located(self.locator)

    def present(self) -> Callable:
        """
        Get the expected condition for the presence of the element(s).

        :return: The expected condition for presence.
        """
        if self.is_many:
            return EC.presence_of_all_elements_located(self.locator)
        else:
            return EC.presence_of_element_located(self.locator)

    def clickable(self) -> Callable:
        """
        Get the expected condition for the element to be clickable.

        :return: The expected condition for clickability.
        """
        return EC.element_to_be_clickable(self.locator)

    @classmethod
    def one(cls, locator: Locator) -> "Element":
        """
        Create an Element instance for a single element.

        :param locator: Locator tuple (By, value) to find the element.
        :return: An Element instance configured for a single element.
        """
        return cls(locator, many=False)

    @classmethod
    def many(cls, locator: Locator) -> "Element":
        """
        Create an Element instance for multiple elements.

        :param locator: Locator tuple (By, value) to find the elements.
        :return: An Element instance configured for multiple elements.
        """
        return cls(locator, many=True)
