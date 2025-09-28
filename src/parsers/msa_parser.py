# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from .base_parser import BaseParser

class MsaParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析MSA数据文件
        
        Returns:
            List[Dict[str, Any]]: MSA数据记录列表
        """
        records = []
        
        for line in self._read_file_lines():
            try:
                record = self._parse_msa_line(line)
                if record:
                    records.append(record)
            except Exception as e:
                self.logger.error(f"解析MSA数据行失败: {line}, 错误: {e}")
                continue
        
        self.validate_data(records)
        return records
    
    def _parse_msa_line(self, line: str) -> Dict[str, Any]:
        """
        解析单行MSA数据
        
        Args:
            line: 数据行
            
        Returns:
            Dict[str, Any]: MSA数据记录
        """
        fields = self._split_line(line)
        
        if len(fields) < 6:
            self.logger.warning(f"MSA数据字段不足: {line}")
            return None
        
        # 解析基本字段
        sector_count = self._safe_int(fields[0])
        navaid_identifier = self._safe_str(fields[1])
        region_code = self._safe_str(fields[2])
        airport_icao = self._safe_str(fields[3])
        msa_type = self._safe_str(fields[4], 'M')
        
        # 验证必要字段
        if not navaid_identifier or not airport_icao:
            self.logger.warning(f"导航台标识符或机场代码为空: {line}")
            return None
        
        # 验证扇区数量
        if sector_count < 1 or sector_count > 3:
            self.logger.warning(f"MSA扇区数量无效: {sector_count}")
            return None
        
        # 初始化记录
        record = {
            'sector_count': sector_count,
            'navaid_identifier': navaid_identifier,
            'region_code': region_code,
            'airport_icao': airport_icao,
            'msa_type': msa_type,
            'sector1_bearing': None,
            'sector1_altitude': None,
            'sector1_radius': None,
            'sector2_bearing': None,
            'sector2_altitude': None,
            'sector2_radius': None,
            'sector3_bearing': None,
            'sector3_altitude': None,
            'sector3_radius': None
        }
        
        # 解析扇区数据
        field_index = 5
        for sector_num in range(1, sector_count + 1):
            if field_index + 2 < len(fields):
                bearing = self._safe_int(fields[field_index])
                altitude = self._safe_int(fields[field_index + 1])
                radius = self._safe_int(fields[field_index + 2])
                
                record[f'sector{sector_num}_bearing'] = bearing
                record[f'sector{sector_num}_altitude'] = altitude
                record[f'sector{sector_num}_radius'] = radius
                
                field_index += 3
            else:
                self.logger.warning(f"MSA扇区{sector_num}数据不足: {line}")
                break
        
        return record
