#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_DIR/src"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "错误: 未找到Python"
    exit 1
fi

cd "$SRC_DIR" || exit 1
$PYTHON_CMD main.py -t airports,waypoints,airways,navaids

if [ $? -eq 0 ]; then
    echo "✓ 快速转换完成"
else
    echo "✗ 转换失败"
    exit 1
fi
