from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socket = SocketIO(app)

# ruff: noqa
import auto_resume.vite_proxy
import auto_resume.views 