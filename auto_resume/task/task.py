from abc import ABC, abstractmethod
from auto_resume.model.context import AppContext

class Task(ABC):
    ctx: AppContext

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx = ctx


    @property
    def db(self):
        return self.ctx.db

    @property
    def config(self):
        return self.ctx.config


    @abstractmethod
    async def execute():
        pass
