# 数据集目录整理脚本
# 运行此脚本整理数据集目录结构

@echo off
chcp 65001 >nul
echo ========================================
echo    数据集目录整理
echo ========================================

set "SOURCE=d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\dataset\Tomato\tomato"
set "DEST=d:\Develop\CODE\AIWORK\Projects\yolo-detection-system\dataset\Tomato"

echo.
echo [1/5] 创建目标目录...
mkdir "%DEST%\images\train" 2>nul
mkdir "%DEST%\images\val" 2>nul
mkdir "%DEST%\labels\train" 2>nul
mkdir "%DEST%\labels\val" 2>nul

echo.
echo [2/5] 复制训练集图片...
xcopy /E /Y "%SOURCE%\images\train\*.*" "%DEST%\images\train\"

echo.
echo [3/5] 复制验证集图片...
xcopy /E /Y "%SOURCE%\images\val\*.*" "%DEST%\images\val\"

echo.
echo [4/5] 复制训练集标注...
xcopy /E /Y "%SOURCE%\labels\train\*.*" "%DEST%\labels\train\"

echo.
echo [5/5] 检查验证集标注...
if not exist "%SOURCE%\labels\val" (
    echo    警告: 原始数据集没有验证集标注!
    echo    解决方案: 将从训练集中划分 20%% 作为验证集
    echo    按任意键继续...
    pause
)

echo.
echo ========================================
echo    目录整理完成！
echo ========================================
echo.
echo    新目录结构:
echo    - images/train/  - images/val/
echo    - labels/train/ - labels/val/
echo.
echo    接下来请修改 data.yaml 并上传到服务器
echo ========================================

pause
