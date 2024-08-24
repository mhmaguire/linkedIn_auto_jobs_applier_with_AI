import { io } from 'socketio'

const socket = io()

socket.on('connect', () => {
  console.log('connected socket io!')
  socket.emit('myevent', {data: 'connected'})
})