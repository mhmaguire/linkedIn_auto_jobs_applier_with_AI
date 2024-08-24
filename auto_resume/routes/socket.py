from time import sleep
from auto_resume import socketio, app

from threading import Thread


class Task:

    def __init__(self, name) -> None:
        self.name = name
    
    def perform(self):
        for i in range(100):
            print(i)
            socketio.emit('progress', {'progress': i, 'task_name': self.name})
            sleep(1)
            

    @classmethod
    def run(cls, task_name):
        cls(task_name).perform()
        

@app.route('/tasks/<task_name>', methods=['POST'])
def task(task_name):
    print('task', task_name)

    Thread(target=Task.run, args=(task_name, )).start()

    return 'started task'

    


@socketio.on('connect')
def connected():
    print('CONNECTED')
    

@socketio.on('message')
def message(data):
    print('ON MESSAGE', data)