from flask import jsonify, render_template, request

from auto_resume import app
from auto_resume.model.config import Parameters


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404


@app.route('/api/search/parameters', methods=['GET', 'PUT'])
def search_parameters():
    if request.method == 'PUT':
        Parameters.update(request.get_json())

        return {'success': True}, 200
    else: 
        return {'parameters': Parameters.load().model_dump(by_alias=True)}
    




@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return render_template("index.html.j2")
