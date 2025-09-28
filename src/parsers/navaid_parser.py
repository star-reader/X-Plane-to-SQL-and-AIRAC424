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
        frequency = self._safe_int(fields[4])
        range_nm = self._safe_int(fields[5])
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
        # 不同类型导航设备的频率范围
        frequency_ranges = {
            2: (190, 1750),    # NDB: 190-1750 kHz
            3: (108000, 118000),  # VOR: 108-118 MHz (转换为kHz)
            4: (108000, 112000),  # ILS LOC: 108-112 MHz
            5: (108000, 112000),  # ILS GS: 108-112 MHz
            6: (75000, 76000),    # OM: 75 MHz
            7: (75000, 76000),    # MM: 75 MHz
            8: (75000, 76000),    # IM: 75 MHz
            12: (960000, 1215000), # DME: 960-1215 MHz (转换为kHz)
            13: (1030000, 1090000) # TACAN: 1030-1090 MHz
        }
        
        if nav_type not in frequency_ranges:
            return True  # 未知类型，不验证
        
        min_freq, max_freq = frequency_ranges[nav_type]
        return min_freq <= frequency <= max_freq
