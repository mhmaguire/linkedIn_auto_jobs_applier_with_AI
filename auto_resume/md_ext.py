from textwrap import dedent

from jinja2 import nodes
from jinja2.environment import Environment
from jinja2.ext import Extension
from markdown import Markdown

from auto_resume import app


class MarkdownExt(Extension):
    tags = {"markdown"}

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        self.renderer = Markdown()

    def parse(self, parser):
        line = next(parser.stream).lineno
        body = parser.parse_statements(["name:endmarkdown"], drop_needle=True)

        return nodes.CallBlock(self.call_method("_render_md"), [], [], body).set_lineno(
            line
        )

    def _render_md(self, caller):
        source = str.strip(dedent(caller()))
        output = self.renderer.convert(source)
        return output


@app.template_filter("md")
def mkdn(s):
    return Markdown().convert(s)


app.jinja_env.add_extension(MarkdownExt)
