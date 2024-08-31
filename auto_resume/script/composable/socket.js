import socket from '@/socket.js'

export function useSocket() {

  const state = reactive({
    connected: false
  })

  socket.on('connect', () => {
    console.log('connected socket io!')
    state.connected = true
  })

  socket.on('progress', (data) => {
    state.connected = false
  })

  return {
    on: socket.on.bind(socket),
    state
  }
}

