import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'

/** @type {import('vite').UserConfig} */
export default {
  root: resolve('auto_resume/script/'),
  appType: 'custom', 
  server: {
    port: 5173,
    strictPort: true,
  },
  plugins: [
    vue()
  ],
  build: {
    manifest: true,
    rollupOptions: {
      input: resolve('auto_resume/script/index.js')
    },
    outDir: 'static'
  },
  resolve: {
    alias: {
      '@': resolve('auto_resume/script/')
    }
  }
}