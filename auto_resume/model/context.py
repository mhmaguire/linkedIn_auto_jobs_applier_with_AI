import asyncio
from contextlib import asynccontextmanager

from auto_resume.model.config import Config, Files
from prisma import Prisma


class AppContext:
    def __init__(self) -> None:
        self.config = None
        self.db = Prisma(auto_register=True)

    async def asetup(self):
        Files.init()
        self.config = Config.load()
        await self.db.connect()
        return self

    def setup(self):
        return asyncio.run(self.asetup())

    async def ateardown(self):
        await self.db.disconnect()

    def teardown(self):
        asyncio.run(self.ateardown())
        

    async def __aenter__(self):
        return await self.asetup()

    async def __aexit__(self):
        await self.ateardown()

    def __enter__(self):
        return self.setup()

    def __exit__(self):
        self.teardown()

@asynccontextmanager
async def app():
    ctx = AppContext()
    try:
        yield await ctx.__aenter__()
    finally:
        await ctx.__aexit__()