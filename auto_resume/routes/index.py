from flask import jsonify, render_template

from auto_resume import app


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html.j2")
