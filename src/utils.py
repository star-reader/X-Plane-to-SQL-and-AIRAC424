# -*- coding: utf-8 -*-
import os
import re
from typing import Union, Optional

def validate_icao_code(icao_code: str) -> bool:
    """
    验证ICAO机场代码格式
    """
    if not icao_code or len(icao_code) != 4:
        return False
    
    # ICAO代码应该是4个字母或数字，转换为大写后检查
    return re.match(r'^[A-Z0-9]{4}$', icao_code.upper()) is not None

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    验证坐标是否在有效范围内
    """
    return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

def format_altitude(altitude: Union[int, str]) -> str:
    """
    格式化高度显示
    """
    if isinstance(altitude, str):
        return altitude
    
    if altitude == -1:
        return "未设置"
    elif altitude >= 18000:
        fl = altitude // 100
        return f"FL{fl}"
    else:
        return f"{altitude}ft"

def safe_filename(filename: str) -> str:
    """
    生成安全的文件名
    """
    # 移除或替换不安全的字符
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return safe_chars.strip()

def ensure_directory(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_file_size_mb(file_path: str) -> float:
    """
    获取文件大小（MB）
    """
    if not os.path.exists(file_path):
        return 0.0
    
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def parse_frequency(freq_str: str) -> Optional[int]:
    """
    解析频率字符串
    """
    try:
        freq = float(freq_str)
        
        # 如果频率小于1000，可能是MHz，需要转换为kHz
        if freq < 1000:
            freq = freq * 1000
        
        return int(freq)
    except (ValueError, TypeError):
        return None

def format_duration(seconds: float) -> str:
    """
    格式化时间间隔显示
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
