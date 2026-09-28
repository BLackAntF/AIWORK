/**
 * 小程序构建脚本（mp-weixin）
 *
 * 用途：
 * 1. 自动探测本机局域网 IPv4 并注入 VITE_API_BASE_URL，真机调试时手机可访问电脑上的后端，
 *    不再需要手动改 .env 里的 IP（DHCP 换 IP 也无需改代码）。
 * 2. 输出目录固定为默认 dist/build/mp-weixin（--dev 时为 dist/dev/mp-weixin），
 *    微信开发者工具导入后无需重新导入，重新点击「编译」即可。
 */
const { spawnSync } = require('child_process')
const os = require('os')

const IS_DEV = process.argv.includes('--dev')
const PLATFORM = process.argv.includes('--platform=app') ? 'app' : 'mp-weixin'

function detectLanIp() {
  const candidates = []
  const ifaces = os.networkInterfaces()
  for (const name of Object.keys(ifaces)) {
    for (const net of ifaces[name] || []) {
      if (net.family !== 'IPv4' || net.internal) continue
      candidates.push({ name, address: net.address })
    }
  }
  // 优先常见私网网段：192.168.x / 10.x / 172.16-31.x
  return (
    candidates.find(c => /^192\.168\./.test(c.address)) ||
    candidates.find(c => /^10\./.test(c.address)) ||
    candidates.find(c => /^172\.(1[6-9]|2\d|3[01])\./.test(c.address)) ||
    candidates[0]
  )
}

const lan = detectLanIp()
const env = { ...process.env }
if (lan) {
  env.VITE_API_BASE_URL = `http://${lan.address}:5000/api`
}

console.log(`[build-mp-weixin] 局域网 IP: ${lan ? lan.address : '未检测到（使用 .env 默认值）'}`)
console.log(`[build-mp-weixin] API 基地址: ${env.VITE_API_BASE_URL || '(来自 .env)'}`)
console.log(`[build-mp-weixin] 构建平台: ${PLATFORM}`)
console.log(`[build-mp-weixin] 构建模式: ${IS_DEV ? 'dev' : 'build'}`)

const bin = process.platform === 'win32' ? 'uni.cmd' : 'uni'
const args = IS_DEV ? ['-p', PLATFORM] : ['build', '-p', PLATFORM]
const result = spawnSync(bin, args, {
  stdio: 'inherit',
  env,
  shell: process.platform === 'win32'
})

process.exit(result.status === null ? 1 : result.status)
