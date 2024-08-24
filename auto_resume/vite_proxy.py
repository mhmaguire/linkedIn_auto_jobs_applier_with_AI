from flask import request, Response

from auto_resume import app

from requests import get

VITE_SERVER = "http://localhost:5173"

@app.route("/<path:path>", methods=["GET"])
def proxy(path):
    url = f"{VITE_SERVER}/{path}"
    proxy_headers = dict(request.headers)

    proxy_request = get(
        url,
        params=request.args,
        stream=True,
        headers=proxy_headers,
        allow_redirects=False,
    )

    headers = dict(proxy_request.raw.headers)

    def generate():
        for chunk in proxy_request.raw.stream(decode_content=False):
            yield chunk

    out = Response(generate(), headers=headers)
    out.status_code = proxy_request.status_code

    return out

