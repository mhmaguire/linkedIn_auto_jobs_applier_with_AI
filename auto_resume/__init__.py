from flask import Flask, g
from flask_socketio import SocketIO
import prisma

def get_db():
    db = prisma.Prisma()
    if not db.is_connected():
        db.connect()
    return db
    

prisma.register(get_db)

app = Flask(__name__)


@app.teardown_appcontext
def teardown(_):
    print('TEARDOWN')
    prisma.get_client().disconnect()


socketio = SocketIO(app)

# ruff: noqa
import auto_resume.routes.vite
import auto_resume.routes.md_ext
import auto_resume.routes.job
import auto_resume.routes.resume
import auto_resume.routes.socket
import auto_resume.routes.index
