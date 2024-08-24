from abc import ABC, abstractmethod

class Site(ABC):
    @abstractmethod
    def authenticate(self, driver):
        pass

    @abstractmethod
    def search(self, driver):
        pass

    @abstractmethod
    def job(self, driver, job_id):
        pass