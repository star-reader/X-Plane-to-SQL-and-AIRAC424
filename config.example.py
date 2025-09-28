# -*- coding: utf-8 -*-
"""

重命名为config.py生效
"""

SOURCE_CONFIG = {
    # 导航数据目录
    'source_directory': '../source',
    # CIFP数据目录 (相对于source_directory)
    'cifp_directory': 'CIFP',
    
    # 数据文件映射
    'data_files': {
        'airports': 'earth_aptmeta.dat',
        'airways': 'earth_awy.dat',
        'waypoints': 'earth_fix.dat',
        'holdings': 'earth_hold.dat',
        'navaids': 'earth_nav.dat',
        'mora': 'earth_mora.dat',
        'msa': 'earth_msa.dat'
    }
}

OUTPUT_CONFIG = {
    'output_directory': '../output',
    'main_sql_file': 'navdata.sql',
    'generate_separate_files': False,
    'encoding': 'utf-8',
    'batch_size': 1000
}

PARSING_CONFIG = {
    # 是否启用数据验证
    'enable_validation': True,
    # 是否跳过错误记录
    'skip_invalid_records': True,
    # 最大错误记录数（超过此数量将停止解析）
    'max_errors': 1000,
    # 是否解析终端程序数据（因为CIFP太大了）
    'parse_terminal_procedures': True,
    # 终端程序数据限制
    'terminal_procedures_limit': 0
}


LOGGING_CONFIG = {
    'level': 'INFO',
    'log_file': 'conversion.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'console_output': True
}

# 这个目前还没做
DATABASE_CONFIG = {
    'type': 'mysql',
    'connection': {
        'host': 'localhost',
        'port': 3306,
        'database': 'navdata',
        'username': 'root',
        'password': '', 
        'charset': 'utf8mb4'
    },
    'truncate_tables': True,
    'use_transaction': True
}

PERFORMANCE_CONFIG = {
    # 多进程
    'enable_multiprocessing': False,
    'process_count': 0,
    'memory_limit': 1024,
    'show_progress': True
}
