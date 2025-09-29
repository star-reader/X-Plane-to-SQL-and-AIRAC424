# -*- coding: utf-8 -*-
import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator

class BaseParser(ABC):
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 验证文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    def _read_file_lines(self) -> Iterator[str]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # 跳过空行、注释行和结束标记
                    if not line or line.startswith('I') or line.startswith('#'):
                        continue
                    
                    # 跳过版本信息行
                    if 'Version - data cycle' in line:
                        continue
                    
                    # 跳过文件结束标记
                    if line.strip() == '99':
                        continue
                    
                    yield line
                    
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用latin-1编码
            self.logger.warning(f"UTF-8解码失败，尝试使用latin-1编码: {self.file_path}")
            with open(self.file_path, 'r', encoding='latin-1') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    if not line or line.startswith('I') or line.startswith('#'):
                        continue
                    
                    if 'Version - data cycle' in line:
                        continue
                    
                    # 跳过文件结束标记
                    if line.strip() == '99':
                        continue
                    
                    yield line
    
    def _split_line(self, line: str, delimiter: str = None) -> List[str]:
        if delimiter:
            return [field.strip() for field in line.split(delimiter)]
        else:
            # 使用空格分割，但保留多个连续空格的含义
            return line.split()
    
    def _safe_int(self, value: str, default: int = 0) -> int:
        try:
            return int(value) if value and value.strip() != '' else default
        except (ValueError, TypeError):
            self.logger.warning(f"无法转换为整数: {value}, 使用默认值: {default}")
            return default
    
    def _safe_float(self, value: str, default: float = 0.0) -> float:
        try:
            return float(value) if value and value.strip() != '' else default
        except (ValueError, TypeError):
            self.logger.warning(f"无法转换为浮点数: {value}, 使用默认值: {default}")
            return default
    
    def _safe_str(self, value: str, default: str = '') -> str:
        return value.strip() if value else default
    
    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        pass
    
    def get_record_count(self) -> int:
        count = 0
        for _ in self._read_file_lines():
            count += 1
        return count
    
    def validate_data(self, records: List[Dict[str, Any]]) -> bool:
        if not records:
            self.logger.warning("没有解析到任何数据记录")
            return False
        
        self.logger.info(f"成功解析 {len(records)} 条记录")
        return True
