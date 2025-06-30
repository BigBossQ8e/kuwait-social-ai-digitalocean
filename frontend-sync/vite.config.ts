import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: [
      '@emotion/react',
      '@emotion/styled',
      '@mui/system',
      '@mui/icons-material',
    ],
    esbuildOptions: {
      // Increase the file descriptor limit
      keepNames: true,
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable sourcemaps in production
    chunkSizeWarningLimit: 3000,
    rollupOptions: {
      maxParallelFileOps: 2, // Limit concurrent file operations
      onwarn(warning, warn) {
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE') {
          return;
        }
        warn(warning);
      }
    }
  },
  // Development server configuration
  server: {
    port: 5173,
    // Proxy is ONLY for development - will not work in production
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
