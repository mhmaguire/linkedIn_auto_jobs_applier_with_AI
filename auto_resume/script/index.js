import '@/style.css'

import './socket.js'

import router from './router.js'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import VueMarkdown from 'vue-markdown-render'

import App from './App.vue'

const pinia = createPinia()

console.log(VueMarkdown)

createApp(App)
  .use(router)
  .use(pinia)
  .mount('#app')
