#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选项:
    -s, --source DIR     源数据目录路径 (默认: ../source)
    -o, --output FILE    输出SQL文件路径 (默认: ../output/navdata.sql)
    -t, --tables LIST   指定要处理的表 (逗号分隔, 默认: 全部)
    -v, --verbose        详细输出模式
    -h, --help          显示帮助信息
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers import (
    AirportParser, AirwayParser, WaypointParser, HoldingParser,
    NavaidParser, MoraParser, MsaParser, TerminalParser
)
from sql_generator import SqlGenerator

class XPlaneConverter:
    
    def __init__(self, source_dir: str, output_file: str, verbose: bool = False):
        self.source_dir = source_dir
        self.output_file = output_file
        self.verbose = verbose
        
        # 设置日志
        self._setup_logging()
        
        # 验证源目录
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"源数据目录不存在: {source_dir}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"初始化转换器: 源目录={source_dir}, 输出文件={output_file}")
    
    def _setup_logging(self):
        level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('conversion.log', encoding='utf-8')
            ]
        )
    
    def convert_all(self, selected_tables: List[str] = None) -> None:
        start_time = datetime.now()
        self.logger.info("开始数据转换...")
        
        # 定义所有可用的表和对应的解析器
        all_tables = {
            'airports': self._parse_airports,
            'airways': self._parse_airways,
            'waypoints': self._parse_waypoints,
            'holdings': self._parse_holdings,
            'navaids': self._parse_navaids,
            'mora': self._parse_mora,
            'msa': self._parse_msa,
            'terminal_procedures': self._parse_terminal_procedures
        }
        
        # 确定要处理的表
        if selected_tables:
            tables_to_process = {k: v for k, v in all_tables.items() if k in selected_tables}
        else:
            tables_to_process = all_tables
        
        # 解析数据
        data_dict = {}
        for table_name, parser_func in tables_to_process.items():
            try:
                self.logger.info(f"开始解析 {table_name} 数据...")
                data_dict[table_name] = parser_func()
                self.logger.info(f"完成解析 {table_name} 数据: {len(data_dict[table_name])} 条记录")
            except Exception as e:
                self.logger.error(f"解析 {table_name} 数据失败: {e}")
                data_dict[table_name] = []
        
        # 生成SQL文件
        self.logger.info("开始生成SQL文件...")
        sql_generator = SqlGenerator(self.output_file)
        sql_generator.generate_complete_sql(data_dict)
        
        # 输出统计信息
        stats = sql_generator.get_statistics(data_dict)
        self._print_statistics(stats)
        
        end_time = datetime.now()
        duration = end_time - start_time
        self.logger.info(f"数据转换完成，耗时: {duration}")
    
    def _parse_airports(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_aptmeta.dat')
        parser = AirportParser(file_path)
        return parser.parse()
    
    def _parse_airways(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_awy.dat')
        parser = AirwayParser(file_path)
        return parser.parse()
    
    def _parse_waypoints(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_fix.dat')
        parser = WaypointParser(file_path)
        return parser.parse()
    
    def _parse_holdings(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_hold.dat')
        parser = HoldingParser(file_path)
        return parser.parse()
    
    def _parse_navaids(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_nav.dat')
        parser = NavaidParser(file_path)
        return parser.parse()
    
    def _parse_mora(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_mora.dat')
        parser = MoraParser(file_path)
        return parser.parse()
    
    def _parse_msa(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.source_dir, 'earth_msa.dat')
        parser = MsaParser(file_path)
        return parser.parse()
    
    def _parse_terminal_procedures(self) -> List[Dict[str, Any]]:
        cifp_dir = os.path.join(self.source_dir, 'CIFP')
        parser = TerminalParser(cifp_dir)
        return parser.parse()
    
    def _print_statistics(self, stats: Dict[str, int]) -> None:
        print("\n" + "="*60)
        print("数据转换统计信息")
        print("="*60)
        
        table_names = {
            'airports': '机场',
            'airways': '航路',
            'waypoints': '航路点',
            'holdings': '等待航线',
            'navaids': '导航设备',
            'mora': 'MORA',
            'msa': 'MSA',
            'terminal_procedures': '终端程序'
        }
        
        for table_name, count in stats.items():
            if table_name != 'total':
                chinese_name = table_names.get(table_name, table_name)
                print(f"{chinese_name:12}: {count:8,} 条记录")
        
        print("-" * 60)
        print(f"{'总计':12}: {stats.get('total', 0):8,} 条记录")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description='X-Plane导航数据转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""
    )
    
    parser.add_argument(
        '-s', '--source',
        default='../source',
        help='源数据目录路径 (默认: ../source)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='../output/navdata.sql',
        help='输出SQL文件路径 (默认: ../output/navdata_data.sql)'
    )
    
    parser.add_argument(
        '-t', '--tables',
        help='指定要处理的表 (逗号分隔), 可选: airports,airways,waypoints,holdings,navaids,mora,msa,terminal_procedures'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细输出模式'
    )
    
    args = parser.parse_args()
    
    # 解析选择的表
    selected_tables = None
    if args.tables:
        selected_tables = [table.strip() for table in args.tables.split(',')]
        
        # 验证表名
        valid_tables = {
            'airports', 'airways', 'waypoints', 'holdings',
            'navaids', 'mora', 'msa', 'terminal_procedures'
        }
        
        invalid_tables = set(selected_tables) - valid_tables
        if invalid_tables:
            print(f"错误: 无效的表名: {', '.join(invalid_tables)}")
            print(f"有效的表名: {', '.join(sorted(valid_tables))}")
            sys.exit(1)
    
    try:
        # 创建转换器并执行转换
        converter = XPlaneConverter(args.source, args.output, args.verbose)
        converter.convert_all(selected_tables)
        
        print(f"\n转换完成! SQL文件已保存到: {args.output}")
        
    except Exception as e:
        print(f"转换失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
