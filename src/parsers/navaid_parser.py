# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from .base_parser import BaseParser

class NavaidParser(BaseParser):
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析导航设备数据文件
        
        Returns:
            List[Dict[str, Any]]: 导航设备数据记录列表
        """
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_navaid_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析导航设备数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_navaid_line(self, line: str) -> Dict[str, Any]:
        """
        解析单行导航设备数据
        
        Args:
            line: 数据行
            
        Returns:
            Dict[str, Any]: 导航设备数据记录
        """
        fields = self._split_line(line)
        
        if len(fields) < 11:
            self.logger.warning(f"导航设备数据字段不足: {line}")
            return None
        
        # 解析基本字段
        nav_type = self._safe_int(fields[0])
        latitude = self._safe_float(fields[1])
        longitude = self._safe_float(fields[2])
        elevation = self._safe_int(fields[3])
        frequency = int(self._safe_float(fields[4]))  # 先转浮点数再转整数，处理57.0这种格式
        range_nm = int(self._safe_float(fields[5]))   # 同样处理
        magnetic_variation = self._safe_float(fields[6])
        identifier = self._safe_str(fields[7])
        usage_type = self._safe_str(fields[8])
        region_code = self._safe_str(fields[9])
        
        # 名称可能包含空格，需要特殊处理
        name = ' '.join(fields[10:]) if len(fields) > 10 else ''
        
        # 验证必要字段
        if not identifier or nav_type == 0:
            self.logger.warning(f"导航台标识符或类型为空: {line}")
            return None
        
        # 验证坐标范围
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            self.logger.warning(f"导航台坐标超出有效范围: {identifier}, lat={latitude}, lon={longitude}")
            return None
        
        # 验证频率范围（根据导航设备类型）
        if not self._validate_frequency(nav_type, frequency):
            self.logger.warning(f"导航台频率超出有效范围: {identifier}, type={nav_type}, freq={frequency}")
        
        return {
            'nav_type': nav_type,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'frequency': frequency,
            'range_nm': range_nm,
            'magnetic_variation': magnetic_variation,
            'identifier': identifier,
            'usage_type': usage_type,
            'region_code': region_code,
            'name': name
        }
    
    def _validate_frequency(self, nav_type: int, frequency: int) -> bool:
        """
        验证导航设备频率是否在有效范围内
        
        Args:
            nav_type: 导航设备类型
            frequency: 频率 (kHz)
            
        Returns:
            bool: 频率是否有效
        """
        # 不同类型导航设备的频率范围 (根据实际数据格式调整)
        # 注意：频率存储格式为5位数字，如116.30MHz存储为11630
        frequency_ranges = {
            2: (100, 2000),       # NDB: 更宽范围适应实际数据
            3: (10000, 12000),    # VOR: 适应实际存储范围 (100-120 MHz)
            4: (10000, 12000),    # ILS LOC: 适应实际存储范围
            5: (10000, 12000),    # ILS GS: 适应实际存储范围
            6: (10000, 12000),    # GS/OM: 扩大范围包含11095等频率
            7: (7000, 12000),     # MM: 扩大范围
            8: (7000, 12000),     # IM: 扩大范围
            12: (10000, 13000),   # DME: 扩大范围适应实际数据
            13: (10000, 13000)    # TACAN: 扩大范围适应实际数据
        }
        
        if nav_type not in frequency_ranges:
            return True  # 未知类型，不验证
        
        min_freq, max_freq = frequency_ranges[nav_type]
        return min_freq <= frequency <= max_freq
