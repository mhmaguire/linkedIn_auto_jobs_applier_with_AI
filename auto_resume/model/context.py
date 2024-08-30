from contextlib import contextmanager

from langchain_community.graphs import Neo4jGraph

import auto_resume.model as model
import prisma
from auto_resume.model.config import Config, Files
from auto_resume.page.util import init_browser


class AppContext:
    def __init__(self) -> None:
        Files.init()
        self.config = None
        self.db = prisma.get_client()
        self.model = model
        self.driver = None
        self.graph = Neo4jGraph()

    def browser(self):
        if self.driver is None:
            self.driver = init_browser()

        return self

    def setup(self):
        self.config = Config.load()
        if not self.db.is_connected():
            self.db.connect()

        return self

    def teardown(self):
        if self.db.is_connected():
            self.db.disconnect()

        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self.setup()

    def __exit__(self):
        self.teardown()


@contextmanager
def app():
    ctx = AppContext()
    try:
        yield ctx.__enter__()
    finally:
        ctx.__exit__()
