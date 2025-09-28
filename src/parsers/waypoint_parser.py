# -*- coding: utf-8 -*-

from typing import List, Dict, Any
from .base_parser import BaseParser

class WaypointParser(BaseParser):
    """
    航路点数据解析器
    解析格式: LAT LON WAYPOINT_NAME USAGE_TYPE REGION_CODE SECTION_CODE WAYPOINT_ID
    
    示例行: -1.000000000  -10.000000000  0110W ENRT GO 2115159 01S010W
    """
    
    def parse(self) -> List[Dict[str, Any]]:
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_waypoint_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析航路点数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_waypoint_line(self, line: str) -> Dict[str, Any]:
        fields = self._split_line(line)
        
        if len(fields) < 7:
            self.logger.warning(f"航路点数据字段不足: {line}")
            return None
        
        # 解析基本字段
        latitude = self._safe_float(fields[0])
        longitude = self._safe_float(fields[1])
        waypoint_name = self._safe_str(fields[2])
        usage_type = self._safe_str(fields[3])
        region_code = self._safe_str(fields[4])
        section_code = self._safe_int(fields[5])
        waypoint_id = self._safe_str(fields[6])
        
        # 验证必要字段
        if not waypoint_name or not usage_type:
            self.logger.warning(f"航路点名称或使用类型为空: {line}")
            return None
        
        # 验证坐标范围
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            self.logger.warning(f"航路点坐标超出有效范围: {waypoint_name}, lat={latitude}, lon={longitude}")
            return None
        
        # 根据使用类型判断是否为终端航路点
        is_terminal = self._is_terminal_waypoint(usage_type)
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'waypoint_name': waypoint_name,
            'usage_type': usage_type,
            'region_code': region_code,
            'section_code': section_code,
            'waypoint_id': waypoint_id,
            'is_terminal': is_terminal
        }
    
    def _is_terminal_waypoint(self, usage_type: str) -> bool:

        # 终端区域相关的使用类型
        terminal_types = ['TERM', 'APP', 'DEP', 'SID', 'STAR']
        
        # 检查使用类型是否包含终端相关关键词
        for terminal_type in terminal_types:
            if terminal_type in usage_type.upper():
                return True
        
        # ENRT表示航路点，通常不是终端点
        if usage_type.upper() == 'ENRT':
            return False
        
        # 其他情况根据具体需求判断
        return False
