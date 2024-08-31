import { createStore } from 'vue'
import socket from '@/socket'

export const useConnection = createStore('connection', () => {

  const connected = ref(false)

  socket.on('connected', () => connected.value = true)
  socket.on('disconnected', () => connected.value = false)

  return {
    connected
  }
})