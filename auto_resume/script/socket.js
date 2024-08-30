import '@/style.css'
import 'vite/modulepreload-polyfill'
import { io } from 'socket.io-client'

const socket = io({transports: ['websocket', 'polling']})

socket.on('connect', () => {
  console.log('connected socket io!')
  socket.emit('message', {data: 'connected'})
})

socket.on('progress', (data) => {
  console.log(data)
})