from contextlib import asynccontextmanager
from model.config import Config, Files

from prisma import Prisma


class AppContext:
    def __init__(self) -> None:
        self.config = None
        self.db = Prisma(auto_register=True)

    async def __aenter__(self):
        print('entering ctx')
        Files.init()
        self.config = Config.load()
        await self.db.connect()
        return self

    async def __aexit__(self):
        print('exiting ctx')
        await self.db.disconnect()

@asynccontextmanager
async def app():
    ctx = AppContext()
    try:
        yield await ctx.__aenter__()
    finally:
        await ctx.__aexit__()