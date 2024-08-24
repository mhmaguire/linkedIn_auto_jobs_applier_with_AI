from abc import ABC, abstractmethod
from auto_resume.model.context import AppContext
from prisma import Prisma

class Task(ABC):
    ctx: AppContext

    def __init__(self, ctx: AppContext) -> None:
        """
        Initialize the Task with the given application context.

        :param ctx: The application context containing configuration and database access.
        """
        super().__init__()
        self.ctx = ctx

    @property
    def db(self) -> Prisma:
        """
        Get the database client from the application context.

        :return: An instance of the Prisma client.
        """
        return self.ctx.db

    @property
    def config(self) -> dict:
        """
        Get the configuration from the application context.

        :return: A dictionary containing configuration settings.
        """
        return self.ctx.config

    @abstractmethod
    async def execute() -> None:
        """
        Execute the task. This method should be implemented by subclasses.

        :return: None
        """
        pass
