from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# ruff: noqa
import auto_resume.vite
import auto_resume.md_ext
import auto_resume.views
import auto_resume.socket
