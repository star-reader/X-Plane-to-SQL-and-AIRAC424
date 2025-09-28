# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from .base_parser import BaseParser

class AirwayParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_airway_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析航路数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_airway_line(self, line: str) -> Dict[str, Any]:
        fields = self._split_line(line)
        
        if len(fields) < 11:
            self.logger.warning(f"航路数据字段不足: {line}")
            return None
        
        # 解析基本字段
        from_waypoint = self._safe_str(fields[0])
        from_region = self._safe_str(fields[1])
        from_section = self._safe_int(fields[2])
        to_waypoint = self._safe_str(fields[3])
        to_region = self._safe_str(fields[4])
        to_section = self._safe_int(fields[5])
        airway_type = self._safe_str(fields[6], 'N')
        direction = self._safe_int(fields[7], 1)
        min_altitude = self._safe_int(fields[8])
        max_altitude = self._safe_int(fields[9])
        airway_name = self._safe_str(fields[10])
        
        # 验证必要字段
        if not from_waypoint or not to_waypoint or not airway_name:
            self.logger.warning(f"航路点或航路名称为空: {line}")
            return None
        
        # 验证高度范围
        if min_altitude > max_altitude and max_altitude > 0:
            self.logger.warning(f"最低高度大于最高高度: {airway_name}, min={min_altitude}, max={max_altitude}")
        
        return {
            'from_waypoint': from_waypoint,
            'from_region': from_region,
            'from_section': from_section,
            'to_waypoint': to_waypoint,
            'to_region': to_region,
            'to_section': to_section,
            'airway_type': airway_type,
            'direction': direction,
            'min_altitude': min_altitude,
            'max_altitude': max_altitude,
            'airway_name': airway_name
        }
