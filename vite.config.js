import { resolve } from 'node:path'
import vue from '@vitejs/plugin-vue'
import Inspect from 'vite-plugin-inspect'
import { execa } from 'execa'



const PyPlugin = () => {

  return {
    name: 'py-vite',
    async resolveId(source, importer, options) {
      console.log('PY VITE RESOLVE', source, importer, options)
      // if (source.endsWith('.py')) {
        
      // }

      return null
    },
    async load(id) {
      if (id.endsWith('.py')) {
        console.log('PY VITE LOAD', id)

        const { stdout } = await execa`python -m auto_resume schema`

        return stdout
      }

      return null
    }
  }
}


/** @type {import('vite').UserConfig} */
export default {
  root: resolve('auto_resume/script/'),
  appType: 'custom', 
  server: {
    port: 5173,
    strictPort: true,
  },
  plugins: [
    vue(),
    Inspect(),
    PyPlugin()
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