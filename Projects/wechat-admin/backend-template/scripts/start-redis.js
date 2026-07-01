const { spawn } = require('child_process');
const path = require('path');

const redisPath = 'D:\\Develop\\codeApp\\Redis';
const redisCmd = path.join(redisPath, 'redis-server.exe');
const redisConf = path.join(redisPath, 'redis.windows.conf');

console.log('正在启动 Redis...');

const redis = spawn('cmd.exe', ['/c', 'start', 'cmd', '/k', `redis-server.exe redis.windows.conf`], {
  cwd: redisPath,
  stdio: 'inherit',
  shell: true
});

redis.on('error', (err) => {
  console.error('启动 Redis 失败:', err.message);
  console.log('请手动运行: scripts/start-redis.bat');
});

setTimeout(() => {
  console.log('Redis 启动命令已执行');
  console.log('如果新窗口未打开，请手动运行: scripts/start-redis.bat');
}, 1000);
