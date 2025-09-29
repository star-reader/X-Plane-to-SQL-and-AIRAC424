# -*- coding: utf-8 -*-

import os
from typing import List, Dict, Any
from .base_parser import BaseParser

class TerminalParser(BaseParser):
    def __init__(self, cifp_directory: str):
        """
        初始化
        """
        self.cifp_directory = cifp_directory
        self.logger = self._setup_logger()
        
        if not os.path.exists(cifp_directory):
            raise FileNotFoundError(f"CIFP目录不存在: {cifp_directory}")
    
    def _setup_logger(self):
        import logging
        return logging.getLogger(self.__class__.__name__)
    
    def parse_all_airports(self) -> List[Dict[str, Any]]:
        """
        解析所有机场的终端程序数据
        
        Returns:
            List[Dict[str, Any]]: 所有终端程序数据记录列表
        """
        all_records = []
        
        # 遍历CIFP目录中的所有.dat文件
        for filename in os.listdir(self.cifp_directory):
            if filename.endswith('.dat'):
                airport_icao = filename[:-4]  # 移除.dat扩展名
                file_path = os.path.join(self.cifp_directory, filename)
                
                try:
                    records = self.parse_airport(file_path, airport_icao)
                    all_records.extend(records)
                    self.logger.info(f"成功解析机场 {airport_icao}: {len(records)} 条记录")
                except Exception as e:
                    self.logger.error(f"解析机场 {airport_icao} 失败: {e}")
                    continue
        
        self.logger.info(f"总共解析 {len(all_records)} 条终端程序记录")
        return all_records
    
    def parse_airport(self, file_path: str, airport_icao: str) -> List[Dict[str, Any]]:
        """
        解析单个机场的终端程序数据
        
        Args:
            file_path: 机场数据文件路径
            airport_icao: 机场ICAO代码
            
        Returns:
            List[Dict[str, Any]]: 终端程序数据记录列表
        """
        records = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # 跳过空行
                    if not line:
                        continue
                    
                    try:
                        record = self._parse_terminal_line(line, airport_icao)
                        if record:
                            records.append(record)
                    except Exception as e:
                        self.logger.error(f"解析终端程序数据行失败 {file_path}:{line_num}: {line}, 错误: {e}")
                        continue
                        
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试使用latin-1编码
            self.logger.warning(f"UTF-8解码失败，尝试使用latin-1编码: {file_path}")
            with open(file_path, 'r', encoding='latin-1') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        record = self._parse_terminal_line(line, airport_icao)
                        if record:
                            records.append(record)
                    except Exception as e:
                        self.logger.error(f"解析终端程序数据行失败 {file_path}:{line_num}: {line}, 错误: {e}")
                        continue
        
        return records
    
    def _parse_terminal_line(self, line: str, airport_icao: str) -> Dict[str, Any]:
        """
        解析单行终端程序数据
        
        Args:
            line: 数据行
            airport_icao: 机场ICAO代码
            
        Returns:
            Dict[str, Any]: 终端程序数据记录
        """
        # AIRAC424格式使用逗号分隔，以分号结尾
        if not line.endswith(';'):
            return None
        
        # 移除末尾的分号并按逗号分割
        line = line[:-1]  # 移除分号
        fields = [field.strip() for field in line.split(',')]
        
        # 对于字段不足的情况，先检查是否是RWY记录（跑道信息记录格式不同）
        if len(fields) < 10:
            # 检查是否是RWY记录或其他特殊格式
            if fields and (fields[0].startswith('RWY:') or fields[0].startswith('AIRPORT:')):
                # 跳过这些特殊格式记录，它们不是标准的终端程序记录
                return None
            else:
                # 其他格式不足的记录也跳过
                return None
        
        # 解析程序类型和基本信息
        type_info = fields[0].split(':')
        if len(type_info) != 2:
            return None
        
        procedure_type = type_info[0]
        sequence_number = type_info[1]
        
        # 安全解析其他字段，防止索引超出范围
        route_type = self._safe_int(fields[1]) if len(fields) > 1 else 0
        procedure_name = self._safe_str(fields[2]) if len(fields) > 2 else ''
        transition_name = self._safe_str(fields[3]) if len(fields) > 3 else ''
        waypoint_name = self._safe_str(fields[4]) if len(fields) > 4 else ''
        waypoint_region = self._safe_str(fields[5]) if len(fields) > 5 else ''
        waypoint_section = self._safe_int(fields[6]) if len(fields) > 6 else 0
        waypoint_type = self._safe_str(fields[7]) if len(fields) > 7 else ''
        waypoint_description = self._safe_str(fields[8]) if len(fields) > 8 else ''
        path_terminator = self._safe_str(fields[12]) if len(fields) > 12 else ''
        
        # 解析参考导航台信息
        ref_navaid_identifier = self._safe_str(fields[14]) if len(fields) > 14 else ''
        ref_navaid_region = self._safe_str(fields[15]) if len(fields) > 15 else ''
        ref_navaid_section = self._safe_int(fields[16]) if len(fields) > 16 else None
        ref_navaid_type = self._safe_str(fields[17]) if len(fields) > 17 else ''
        
        # 解析坐标和距离信息
        theta = self._safe_float(fields[19]) if len(fields) > 19 else None
        rho = self._safe_float(fields[20]) if len(fields) > 20 else None
        magnetic_course = self._safe_float(fields[21]) if len(fields) > 21 else None
        distance_time = self._safe_str(fields[22]) if len(fields) > 22 else ''
        
        # 解析高度限制
        altitude_description = self._safe_str(fields[24]) if len(fields) > 24 else ''
        altitude1 = self._safe_str(fields[25]) if len(fields) > 25 else ''
        altitude2 = self._safe_str(fields[26]) if len(fields) > 26 else ''
        transition_altitude = self._safe_str(fields[27]) if len(fields) > 27 else ''
        
        # 解析速度限制
        speed_limit = self._safe_str(fields[29]) if len(fields) > 29 else ''
        
        # 解析其他参数
        vertical_angle = self._safe_float(fields[31]) if len(fields) > 31 else None
        center_fix = self._safe_str(fields[32]) if len(fields) > 32 else ''
        multiple_code = self._safe_str(fields[33]) if len(fields) > 33 else ''
        gnss_fms_indication = self._safe_str(fields[34]) if len(fields) > 34 else ''
        
        return {
            'airport_icao': airport_icao,
            'procedure_type': procedure_type,
            'sequence_number': sequence_number,
            'route_type': route_type,
            'procedure_name': procedure_name,
            'transition_name': transition_name,
            'waypoint_name': waypoint_name,
            'waypoint_region': waypoint_region,
            'waypoint_section': waypoint_section,
            'waypoint_type': waypoint_type,
            'waypoint_description': waypoint_description,
            'path_terminator': path_terminator,
            'ref_navaid_identifier': ref_navaid_identifier,
            'ref_navaid_region': ref_navaid_region,
            'ref_navaid_section': ref_navaid_section,
            'ref_navaid_type': ref_navaid_type,
            'theta': theta,
            'rho': rho,
            'magnetic_course': magnetic_course,
            'distance_time': distance_time,
            'altitude_description': altitude_description,
            'altitude1': altitude1,
            'altitude2': altitude2,
            'transition_altitude': transition_altitude,
            'speed_limit': speed_limit,
            'vertical_angle': vertical_angle,
            'center_fix': center_fix,
            'multiple_code': multiple_code,
            'gnss_fms_indication': gnss_fms_indication
        }
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        实现基类的抽象方法
        
        Returns:
            List[Dict[str, Any]]: 解析后的数据记录列表
        """
        return self.parse_all_airports()
    
    def _safe_str(self, value: str, default: str = '') -> str:
        return value.strip() if value and value.strip() else default
    
    def _safe_int(self, value: str, default: int = 0) -> int:
        try:
            return int(value) if value and value.strip() != '' else default
        except (ValueError, TypeError):
            return default
    
    def _safe_float(self, value: str, default: float = 0.0) -> float:
        try:
            return float(value) if value and value.strip() != '' else default
        except (ValueError, TypeError):
            return default
