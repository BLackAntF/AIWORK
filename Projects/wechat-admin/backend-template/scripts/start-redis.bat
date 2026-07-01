@echo off
REM Redis 启动脚本
REM 启动后请保持此窗口开启

cd /d "D:\Develop\codeApp\Redis"
start cmd /k "redis-server.exe redis.windows.conf"
