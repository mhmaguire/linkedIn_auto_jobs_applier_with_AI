import types
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class Element:

    def __init__(self, locator, many=True):
        self.locator = locator
        self.is_many = many
        self.timeout = 1

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __call__(self, instance, timeout=10, reraise=False):
        try: 
            return instance.wait_for(self.present(), timeout=timeout)
        
        except (NoSuchElementException, TimeoutException) as e:
            if reraise:
                raise e

            return False
            

    def __get__(self, instance, owner):
        if instance is None:
            return self.locator

        return types.MethodType(self, instance)

    def find(self, driver):
        if self.is_many:
            return driver.find_elements(*self.locator)
        else:
            return driver.find_element(*self.locator)

    def visible(self):
        if self.is_many:
            return EC.visibility_of_all_elements_located(self.locator)
        else:
            return EC.visibility_of_element_located(self.locator)

    def present(self):
        if self.is_many:
            return EC.presence_of_all_elements_located(self.locator)
        else:
            return EC.presence_of_element_located(self.locator)

    def clickable(self):
        return EC.element_to_be_clickable(self.locator)

    @classmethod
    def one(cls, locator):
        return cls(locator, many=False)

    @classmethod
    def many(cls, locator):
        return cls(locator, many=True)
