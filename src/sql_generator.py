# -*- coding: utf-8 -*-

import os
import logging
from typing import List, Dict, Any, TextIO
from datetime import datetime

class SqlGenerator:
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.logger = logging.getLogger(self.__class__.__name__)
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_complete_sql(self, data_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        生成完整的SQL文件
        Args:
            data_dict: 包含所有表数据的字典
        """
        with open(self.output_file, 'w', encoding='utf-8') as f:
            self._write_header(f)
            self._write_schema(f)
            self._write_data(f, data_dict)
            self._write_footer(f)
        
        self.logger.info(f"SQL文件生成完成: {self.output_file}")
    
    def _write_header(self, f: TextIO) -> None:
        """
        写入SQL文件头部 
        Args:
            f: 文件对象
        """
        f.write("-- =====================================================\n")
        f.write("-- X-Plane导航数据库转SQL文件\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- =====================================================\n\n")
        
        f.write("-- 设置字符集和存储引擎\n")
        f.write("SET NAMES utf8mb4;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
    
    def _write_schema(self, f: TextIO) -> None:
        """
        写入数据库表结构
        
        Args:
            f: 文件对象
        """
        try:
            from .sql_schemas import get_create_database_sql
        except ImportError:
            # 如果相对导入失败，尝试绝对导入
            from sql_schemas import get_create_database_sql
        
        f.write("-- =====================================================\n")
        f.write("-- 数据库表结构\n")
        f.write("-- =====================================================\n\n")
        
        f.write(get_create_database_sql())
        f.write("\n")
    
    def _write_data(self, f: TextIO, data_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        写入数据INSERT语句
        
        Args:
            f: 文件对象
            data_dict: 数据字典
        """
        f.write("-- =====================================================\n")
        f.write("-- 数据插入语句\n")
        f.write("-- =====================================================\n\n")
        
        # 按表顺序插入数据
        table_order = [
            'airports', 'waypoints', 'navaids', 'airways', 
            'holdings', 'mora', 'msa', 'terminal_procedures'
        ]
        
        for table_name in table_order:
            if table_name in data_dict and data_dict[table_name]:
                self._write_table_data(f, table_name, data_dict[table_name])
    
    def _write_table_data(self, f: TextIO, table_name: str, records: List[Dict[str, Any]]) -> None:
        """
        写入单个表的数据
        
        Args:
            f: 文件对象
            table_name: 表名
            records: 数据记录列表
        """
        if not records:
            return
        
        f.write(f"-- {table_name.upper()} 表数据 ({len(records)} 条记录)\n")
        
        # 获取字段名
        field_names = list(records[0].keys())
        field_names_str = ', '.join(field_names)
        
        # 批量插入，每批1000条记录
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch_records = records[i:i + batch_size]
            
            f.write(f"INSERT INTO {table_name} ({field_names_str}) VALUES\n")
            
            values_list = []
            for record in batch_records:
                values = []
                for field_name in field_names:
                    value = record.get(field_name)
                    values.append(self._format_sql_value(value))
                values_list.append(f"({', '.join(values)})")
            
            f.write(',\n'.join(values_list))
            f.write(";\n\n")
        
        self.logger.info(f"写入 {table_name} 表数据: {len(records)} 条记录")
    
    def _format_sql_value(self, value: Any) -> str:
        """
        格式化SQL值
        
        Args:
            value: 原始值
            
        Returns:
            str: 格式化后的SQL值
        """
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return '1' if value else '0'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # 转义单引号和反斜杠
            escaped_value = value.replace('\\', '\\\\').replace("'", "\\'")
            return f"'{escaped_value}'"
        else:
            # 其他类型转换为字符串
            escaped_value = str(value).replace('\\', '\\\\').replace("'", "\\'")
            return f"'{escaped_value}'"
    
    def _write_footer(self, f: TextIO) -> None:
        """
        写入SQL文件尾部
        
        Args:
            f: 文件对象
        """
        f.write("-- =====================================================\n")
        f.write("-- 数据导入完成\n")
        f.write("-- =====================================================\n\n")
        
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        f.write("-- 数据库导入完成\n")
    
    def generate_table_sql(self, table_name: str, records: List[Dict[str, Any]], 
                          output_file: str = None) -> None:
        """
        生成单个表的SQL文件
        
        Args:
            table_name: 表名
            records: 数据记录列表
            output_file: 输出文件路径，如果为None则使用默认路径
        """
        if output_file is None:
            base_name = os.path.splitext(self.output_file)[0]
            output_file = f"{base_name}_{table_name}.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            self._write_header(f)
            
            # 写入单个表的结构
            try:
                from .sql_schemas import ALL_TABLES
            except ImportError:
                from sql_schemas import ALL_TABLES
            if table_name in ALL_TABLES:
                f.write(f"-- {table_name.upper()} 表结构\n")
                f.write(ALL_TABLES[table_name])
                f.write("\n\n")
            
            # 写入数据
            self._write_table_data(f, table_name, records)
            self._write_footer(f)
        
        self.logger.info(f"单表SQL文件生成完成: {output_file}")
    
    def get_statistics(self, data_dict: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        stats = {}
        total_records = 0
        
        for table_name, records in data_dict.items():
            count = len(records) if records else 0
            stats[table_name] = count
            total_records += count
        
        stats['total'] = total_records
        return stats
