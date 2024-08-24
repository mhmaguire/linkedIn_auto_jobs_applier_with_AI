import { resolve } from 'node:path'

/** @type {import('vite').UserConfig} */
export default {
  root: resolve('app/script/'),
  appType: 'custom', 
  build: {
    manifest: true,
    rollupOptions: {
      input: resolve('app/script/index.js')
    },
    outDir: 'static'
  },
  resolve: {
    alias: {
      '@': resolve('../app/script/')
    }
  }
}