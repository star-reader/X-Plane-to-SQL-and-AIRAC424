#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_DIR/src"
SOURCE_DIR="$PROJECT_DIR/source"
OUTPUT_DIR="$PROJECT_DIR/output"

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        if [[ $(echo "$PYTHON_VERSION >= 3.7" | bc -l) -eq 1 ]]; then
            PYTHON_CMD="python"
        else
            echo "错误: 需要Python 3.7或更高版本"
            exit 1
        fi
    else
        echo "错误: 未找到Python"
        exit 1
    fi
}

check_source_data() {
    if [ ! -d "$SOURCE_DIR" ]; then
        echo "错误: 源数据目录不存在: $SOURCE_DIR"
        echo "请将X-Plane导航数据文件放置在source目录中"
        exit 1
    fi
    
    required_files=("earth_aptmeta.dat" "earth_awy.dat" "earth_fix.dat" "earth_nav.dat")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$SOURCE_DIR/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo "警告: 缺少以下数据文件:"
        printf '  %s\n' "${missing_files[@]}"
        echo "转换将跳过这些数据类型"
    fi
}

create_output_dir() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR"
    fi
}

main() {
    echo "X-Plane导航数据转换工具"
    echo "========================"
    
    check_python
    echo "✓ Python环境: $PYTHON_CMD"
    
    check_source_data
    echo "✓ 源数据目录: $SOURCE_DIR"
    
    create_output_dir
    echo "✓ 输出目录: $OUTPUT_DIR"
    
    echo ""
    echo "开始转换..."
    
    cd "$SRC_DIR" || exit 1
    
    if [ $# -eq 0 ]; then
        $PYTHON_CMD main.py
    else
        $PYTHON_CMD main.py "$@"
    fi
    
    conversion_result=$?
    
    if [ $conversion_result -eq 0 ]; then
        echo ""
        echo "✓ 转换完成"
        echo "SQL文件位置: $OUTPUT_DIR/"
    else
        echo ""
        echo "✗ 转换失败"
        exit 1
    fi
}

main "$@"
