@echo off

setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "SRC_DIR=%PROJECT_DIR%\src"

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python3"
    ) else (
        echo 错误: 未找到Python
        pause
        exit /b 1
    )
)

cd /d "%SRC_DIR%"
%PYTHON_CMD% main.py -t airports,waypoints,airways,navaids

if %errorlevel% equ 0 (
    echo ✓ 快速转换完成
) else (
    echo ✗ 转换失败
    pause
    exit /b 1
)

pause
