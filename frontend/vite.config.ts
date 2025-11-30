import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // ============================================
  // 빌드 최적화 설정
  // ============================================
  build: {
    // 청크 크기 경고 한도 (KB)
    chunkSizeWarningLimit: 500,
    
    // 소스맵 (프로덕션에서는 false)
    sourcemap: false,
    
    // Minify 설정
    minify: 'esbuild',
    
    // CSS 코드 분할
    cssCodeSplit: true,
    
    // Rollup 옵션
    rollupOptions: {
      output: {
        // 벤더 청크 분리 (자주 변경되지 않는 라이브러리)
        manualChunks: {
          // React 관련
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          
          // 상태 관리 & 데이터 fetching
          'vendor-data': ['@tanstack/react-query', 'zustand', 'axios'],
          
          // UI 라이브러리
          'vendor-ui': ['react-hot-toast', 'lucide-react'],
          
          // 차트/시각화 (큰 라이브러리)
          'vendor-charts': ['recharts'],
        },
        
        // 청크 파일명 형식
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    
    // 타겟 브라우저 (모던 브라우저만)
    target: 'es2020',
  },
  
  // ============================================
  // 개발 서버 설정
  // ============================================
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        cookieDomainRewrite: 'localhost',
        secure: false,
      },
    },
  },
  
  // ============================================
  // 최적화 설정
  // ============================================
  optimizeDeps: {
    // 사전 번들링할 의존성
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'zustand',
      'axios',
    ],
  },
  
  // ============================================
  // esbuild 설정
  // ============================================
  esbuild: {
    // 프로덕션에서 console, debugger 제거
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
})