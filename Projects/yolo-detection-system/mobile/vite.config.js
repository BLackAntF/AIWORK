import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    plugins: [
      uni(),
    ],
    server: {
      // 固定 5174 端口（5173 留给 web 前端），避免两个 dev server 抢端口
      port: 5174,
      // 允许局域网/真机访问（手机与电脑同一网络时通过 http://电脑IP:5174 打开 H5）
      host: true,
      // H5 开发模式代理，避免跨域（后端零改动）
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET || 'http://127.0.0.1:5000',
          changeOrigin: true
        }
      }
    }
  }
})
