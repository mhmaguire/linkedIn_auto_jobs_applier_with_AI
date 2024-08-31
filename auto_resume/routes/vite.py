from __future__ import annotations

import glob
from pathlib import Path
from textwrap import dedent

from flask import Response, current_app, request, send_from_directory, url_for
from markupsafe import Markup
from requests import get

from auto_resume import app

VITE_HOST = 'localhost'
VITE_PORT = 5173
ONE_YEAR = 60 * 60 * 24 * 365


# @app.route("/_vite/<path:filename>")
# def proxy(path):
#     url = f"{VITE_SERVER}/{path}"
#     proxy_headers = dict(request.headers)

#     proxy_request = get(
#         url,
#         params=request.args,
#         stream=True,
#         headers=proxy_headers,
#         allow_redirects=False,
#     )

#     headers = dict(proxy_request.raw.headers)

#     def generate():
#         for chunk in proxy_request.raw.stream(decode_content=False):
#             yield chunk

#     out = Response(generate(), headers=headers)
#     out.status_code = proxy_request.status_code

#     return out

@app.route("/_vite/<path:filename>")
def vite_static(
        filename, vite_routes_host: str | None = None  # noqa: ARG002
    ):
        dist = str(_get_root() / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=ONE_YEAR)

def _get_root() -> Path:
    return Path.cwd() / "script"


@app.template_global(name="vite_tags")
def make_tag(*, static: bool = False):
    if static or not current_app.debug:
        tag = make_static_tag()
    else:
        tag = make_debug_tag()

    return Markup(tag)


def make_static_tag():
    js_file_url = url_for("vite_static", filename='index.js')
    css_file_url = url_for("vite_static", filename='style.css')

    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="{js_file_url}"></script>
            <link rel="stylesheet" href="{css_file_url}"></link>
        """
    ).strip()


def make_debug_tag():
    
    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="http://{VITE_HOST}:{VITE_PORT}/@vite/client"></script>
            <script type="module" src="http://{VITE_HOST}:{VITE_PORT}/index.js"></script>
        """
    ).strip()