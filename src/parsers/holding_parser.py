# -*- coding: utf-8 -*-

from typing import List, Dict, Any
from .base_parser import BaseParser

class HoldingParser(BaseParser):
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析等待航线数据文件
        
        Returns:
            List[Dict[str, Any]]: 等待航线数据记录列表
        """
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_holding_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析等待航线数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_holding_line(self, line: str) -> Dict[str, Any]:
        """
        解析单行等待航线数据
        
        Args:
            line: 数据行
            
        Returns:
            Dict[str, Any]: 等待航线数据记录
        """
        fields = self._split_line(line)
        
        if len(fields) < 11:
            self.logger.warning(f"等待航线数据字段不足: {line}")
            return None
        
        # 解析基本字段
        waypoint_name = self._safe_str(fields[0])
        region_code = self._safe_str(fields[1])
        airport_icao = self._safe_str(fields[2])
        section_code = self._safe_int(fields[3])
        inbound_course = self._safe_float(fields[4])
        turn_direction = self._safe_float(fields[5])
        leg_length = self._safe_float(fields[6])
        leg_type = self._safe_str(fields[7], 'R')
        min_altitude = self._safe_int(fields[8])
        max_altitude = self._safe_int(fields[9])
        speed_limit = self._safe_int(fields[10])
        
        # 验证必要字段
        if not waypoint_name or not airport_icao:
            self.logger.warning(f"等待点名称或机场代码为空: {line}")
            return None
        
        # 验证航向范围
        if not (0 <= inbound_course <= 360):
            self.logger.warning(f"入航道向超出有效范围: {waypoint_name}, course={inbound_course}")
        
        # 验证高度范围
        if min_altitude > max_altitude and max_altitude > 0:
            self.logger.warning(f"最低高度大于最高高度: {waypoint_name}, min={min_altitude}, max={max_altitude}")
        
        return {
            'waypoint_name': waypoint_name,
            'region_code': region_code,
            'airport_icao': airport_icao,
            'section_code': section_code,
            'inbound_course': inbound_course,
            'turn_direction': turn_direction,
            'leg_length': leg_length,
            'leg_type': leg_type,
            'min_altitude': min_altitude,
            'max_altitude': max_altitude,
            'speed_limit': speed_limit
        }
