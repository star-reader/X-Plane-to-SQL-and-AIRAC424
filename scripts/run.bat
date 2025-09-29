@echo off

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "SRC_DIR=%PROJECT_DIR%\src"
set "SOURCE_DIR=%PROJECT_DIR%\source"
set "OUTPUT_DIR=%PROJECT_DIR%\output"

:check_python
set "PYTHON_CMD="
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        set "version=%%i"
        for /f "tokens=1,2 delims=." %%a in ("!version!") do (
            if %%a geq 3 (
                if %%a gtr 3 (
                    set "PYTHON_CMD=python"
                ) else if %%b geq 7 (
                    set "PYTHON_CMD=python"
                )
            )
        )
    )
)

if "!PYTHON_CMD!"=="" (
    python3 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=python3"
    )
)

if "!PYTHON_CMD!"=="" (
    echo 错误: 未找到Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查源数据目录
:check_source_data
if not exist "%SOURCE_DIR%" (
    echo 错误: 源数据目录不存在: %SOURCE_DIR%
    echo 请将X-Plane导航数据文件放置在source目录中
    pause
    exit /b 1
)

set "missing_files="
if not exist "%SOURCE_DIR%\earth_aptmeta.dat" set "missing_files=!missing_files! earth_aptmeta.dat"
if not exist "%SOURCE_DIR%\earth_awy.dat" set "missing_files=!missing_files! earth_awy.dat"
if not exist "%SOURCE_DIR%\earth_fix.dat" set "missing_files=!missing_files! earth_fix.dat"
if not exist "%SOURCE_DIR%\earth_nav.dat" set "missing_files=!missing_files! earth_nav.dat"

if not "!missing_files!"=="" (
    echo 警告: 缺少以下数据文件:
    for %%f in (!missing_files!) do echo   %%f
    echo 转换将跳过这些数据类型
)

:create_output_dir
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

:main
echo X-Plane导航数据转换工具
echo ========================

echo ✓ Python环境: !PYTHON_CMD!
echo ✓ 源数据目录: %SOURCE_DIR%
echo ✓ 输出目录: %OUTPUT_DIR%
echo.
echo 开始转换...

cd /d "%SRC_DIR%"

if "%~1"=="" (
    REM 无参数，转换所有数据
    !PYTHON_CMD! main.py
) else (
    REM 传递所有参数
    !PYTHON_CMD! main.py %*
)

set "conversion_result=!errorlevel!"

if !conversion_result! equ 0 (
    echo.
    echo ✓ 转换完成
    echo SQL文件位置: %OUTPUT_DIR%\
) else (
    echo.
    echo ✗ 转换失败
    pause
    exit /b 1
)

pause
