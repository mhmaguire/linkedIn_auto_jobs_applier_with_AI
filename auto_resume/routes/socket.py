

from flask_socketio import emit, Namespace

from multiprocessing import Process, Lock

from auto_resume.task.search import search
from auto_resume import socketio, app


process = None
process_lock = Lock()

def worker(fn, *args, **kwargs):
    return fn(*args, **kwargs)
    

@app.route('/api/tasks/<task_name>', methods=['POST'])
def task(task_name):
    global process
    
    with process_lock:
        if process is None:
            process = Process(target=worker, args=(search,))
            process.start()

    return {'task': {'name': task_name, 'status': 'running'}}, 200


class AutoResumeTasks(Namespace):

    def on_connect(self):
        emit('task_status', {    
            'tasks': [
                {'name': 'Task'}
            ]
        })

    def on_task_status(self):
        emit('task_status', {    
            'tasks': [
                {'name': 'Task'}
            ]
        })

socketio.on_namespace(AutoResumeTasks('/auto_resume'))