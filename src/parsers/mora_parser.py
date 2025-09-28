# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from .base_parser import BaseParser

class MoraParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析MORA数据文件
        
        Returns:
            List[Dict[str, Any]]: MORA数据记录列表
        """
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_mora_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析MORA数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_mora_line(self, line: str) -> Dict[str, Any]:
        """
        解析单行MORA数据
        
        Args:
            line: 数据行
            
        Returns:
            Dict[str, Any]: MORA数据记录
        """
        fields = self._split_line(line)
        
        if len(fields) < 32:  # 2个坐标字段 + 30个高度值
            self.logger.warning(f"MORA数据字段不足: {line}")
            return None
        
        # 解析坐标字段
        lat_str = self._safe_str(fields[0])
        lon_str = self._safe_str(fields[1])
        
        # 转换坐标格式 (+00 -> 0, -45 -> -45)
        latitude_deg = self._parse_coordinate(lat_str)
        longitude_deg = self._parse_coordinate(lon_str)
        
        # 验证坐标范围
        if latitude_deg is None or longitude_deg is None:
            self.logger.warning(f"MORA坐标格式错误: {lat_str}, {lon_str}")
            return None
        
        if not (-90 <= latitude_deg <= 90) or not (-180 <= longitude_deg <= 180):
            self.logger.warning(f"MORA坐标超出有效范围: lat={latitude_deg}, lon={longitude_deg}")
            return None
        
        # 提取高度数据 (30个值)
        grid_data = ' '.join(fields[2:32])
        
        # 验证高度数据
        height_values = fields[2:32]
        if len(height_values) != 30:
            self.logger.warning(f"MORA网格数据不足30个值: {len(height_values)}")
            return None
        
        # 验证所有高度值都是数字
        for i, height in enumerate(height_values):
            if not height.isdigit():
                self.logger.warning(f"MORA高度值不是数字: 位置{i}, 值={height}")
                return None
        
        return {
            'latitude_deg': latitude_deg,
            'longitude_deg': longitude_deg,
            'grid_data': grid_data
        }
    
    def _parse_coordinate(self, coord_str: str) -> int:
        """
        解析坐标字符串
        
        Args:
            coord_str: 坐标字符串 (如 "+00", "-45")
            
        Returns:
            int: 坐标度数，解析失败返回None
        """
        try:
            # 移除符号并转换为整数
            if coord_str.startswith('+'):
                return int(coord_str[1:])
            elif coord_str.startswith('-'):
                return -int(coord_str[1:])
            else:
                return int(coord_str)
        except (ValueError, IndexError):
            return None
