import { io } from 'socket.io-client'

export default io({transports: ['websocket', 'polling']})

