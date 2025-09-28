# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from .base_parser import BaseParser

class AirportParser(BaseParser):
    """
    00AN PA  59.093472222 -156.455833333    80 P  4500 0 18000 FL180
    """
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析机场数据文件
        
        Returns:
            List[Dict[str, Any]]: 机场数据记录列表
        """
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_airport_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析机场数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_airport_line(self, line: str) -> Dict[str, Any]:
        fields = self._split_line(line)
        
        if len(fields) < 10:
            self.logger.warning(f"机场数据字段不足: {line}")
            return None
        
        # 解析基本字段
        icao_code = self._safe_str(fields[0])
        region_code = self._safe_str(fields[1])
        latitude = self._safe_float(fields[2])
        longitude = self._safe_float(fields[3])
        elevation = self._safe_int(fields[4])
        airport_type = self._safe_str(fields[5], 'P')
        runway_length = self._safe_int(fields[6])
        runway_surface = self._safe_str(fields[7], '0')
        transition_altitude = self._safe_int(fields[8], -1)
        transition_level = self._safe_str(fields[9], '-1')
        
        # 验证必要字段
        if not icao_code or not region_code:
            self.logger.warning(f"机场代码或地区代码为空: {line}")
            return None
        
        # 验证坐标范围
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            self.logger.warning(f"机场坐标超出有效范围: {icao_code}, lat={latitude}, lon={longitude}")
            return None
        
        return {
            'icao_code': icao_code,
            'region_code': region_code,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'airport_type': airport_type,
            'runway_length': runway_length,
            'runway_surface': runway_surface,
            'transition_altitude': transition_altitude,
            'transition_level': transition_level
        }
