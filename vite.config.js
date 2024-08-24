import { resolve } from 'node:path'

/** @type {import('vite').UserConfig} */
export default {
  root: resolve('auto_resume/script/'),
  appType: 'custom', 
  server: {
    port: 5173,
    strictPort: true,
  },
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