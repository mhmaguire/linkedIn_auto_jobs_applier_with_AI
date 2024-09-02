import {ref, reactive} from 'vue'
import { defineStore } from 'pinia'

import { io } from 'socket.io-client'



const socket = io('ws://localhost:3000/auto_resume', {transports: ['websocket'], autoConnect: false})

export const useWs = defineStore('connection', () => {
  
  const connected = ref(false)
  const messages = ref([])

  function bind() {
    socket.off()

    socket.on('connect', () => {
      console.log('connected')
      connected.value = true
    })

    socket.on('task_status', (data) => {
      console.log('task_status', data)
    })

    socket.on('connect_error', (error) => {
      console.log(error)
    })
  
    socket.on('disconnect', () => {
      console.log('disconnected')
      connected.value = false
    })
  
    socket.on('message', (data) => {
      messages.value = [...messages.value ,data]
    })


    socket.connect()
  }

  return {
    bind,
    connected,
    messages
  }
})