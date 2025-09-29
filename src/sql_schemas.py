# -*- coding: utf-8 -*-

AIRPORTS_TABLE = """
DROP TABLE IF EXISTS airports;
CREATE TABLE airports (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    icao_code VARCHAR(4) NOT NULL,                    -- ICAO机场代码
    region_code VARCHAR(2) NOT NULL,                  -- 地区代码
    latitude DECIMAL(12, 9) NOT NULL,                 -- 纬度
    longitude DECIMAL(12, 9) NOT NULL,                -- 经度
    elevation INTEGER NOT NULL,                       -- 海拔高度
    airport_type CHAR(1) NOT NULL,                    -- 机场类型 (P=Public, C=Civil, R=Restricted)
    runway_length INTEGER DEFAULT 0,                  -- 跑道长度 (英尺)
    runway_surface CHAR(1) DEFAULT '0',               -- 跑道表面类型 (0=未知, R=沥青，还有其他的导进去在看)
    transition_altitude INTEGER DEFAULT -1,           -- 过渡高度 (英尺, -1表示未设置)
    transition_level VARCHAR(10) DEFAULT '-1',        -- 过渡高度层 (如FL180)
    
    UNIQUE(icao_code),
    KEY idx_airports_icao (icao_code),
    KEY idx_airports_region (region_code),
    KEY idx_airports_location (latitude, longitude)
);
"""

AIRWAYS_TABLE = """
DROP TABLE IF EXISTS airways;
CREATE TABLE airways (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    from_waypoint VARCHAR(5) NOT NULL,                -- 起始航路点
    from_region VARCHAR(2) NOT NULL,                  -- 起始点地区代码
    from_section INTEGER NOT NULL,                    -- 起始点段落代码
    to_waypoint VARCHAR(5) NOT NULL,                  -- 终点航路点
    to_region VARCHAR(2) NOT NULL,                    -- 终点地区代码
    to_section INTEGER NOT NULL,                      -- 终点段落代码
    airway_type CHAR(1) NOT NULL,                     -- 航路类型 (N=Normal, F=Ferry等)
    direction INTEGER NOT NULL,                       -- 方向 (1=单向, 2=双向)
    min_altitude INTEGER NOT NULL,                    -- 最低高度 (百英尺)
    max_altitude INTEGER NOT NULL,                    -- 最高高度 (百英尺)
    airway_name VARCHAR(120) NOT NULL,                -- 航路名称 (可能很长)
    
    KEY idx_airways_from (from_waypoint, from_region),
    KEY idx_airways_to (to_waypoint, to_region),
    KEY idx_airways_name (airway_name),
    KEY idx_airways_type (airway_type)
);
"""


WAYPOINTS_TABLE = """
DROP TABLE IF EXISTS waypoints;
CREATE TABLE waypoints (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    latitude DECIMAL(12, 9) NOT NULL,                 -- 纬度
    longitude DECIMAL(12, 9) NOT NULL,                -- 经度
    waypoint_name VARCHAR(5) NOT NULL,                -- 航路点名称
    usage_type VARCHAR(4) NOT NULL,                   -- 使用类型 (ENRT=航路, TERM=终端等)
    region_code VARCHAR(2) NOT NULL,                  -- 地区代码
    section_code INTEGER NOT NULL,                    -- 段落代码
    waypoint_id VARCHAR(100) NOT NULL,                -- 航路点ID (可能包含描述信息)
    is_terminal BOOLEAN DEFAULT FALSE,                -- 是否为终端航路点 (根据usage_type转换，后面dump成mapbox也要用)
    
    KEY idx_waypoints_name (waypoint_name),
    KEY idx_waypoints_region (region_code),
    KEY idx_waypoints_usage (usage_type),
    KEY idx_waypoints_location (latitude, longitude),
    KEY idx_waypoints_terminal (is_terminal)
);
"""

HOLDINGS_TABLE = """
DROP TABLE IF EXISTS holdings;
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    waypoint_name VARCHAR(5) NOT NULL,                -- 等待点名称
    region_code VARCHAR(2) NOT NULL,                  -- 地区代码
    airport_icao VARCHAR(4) NOT NULL,                 -- 相关机场ICAO代码
    section_code INTEGER NOT NULL,                    -- 段落代码
    inbound_course DECIMAL(5, 1) NOT NULL,            -- 入航道向 (度)
    turn_direction DECIMAL(3, 1) NOT NULL,            -- 转弯方向 (0.0=右转, 1.0=左转)
    leg_length DECIMAL(4, 1) NOT NULL,                -- 航段长度 (海里或分钟)
    leg_type CHAR(1) NOT NULL,                        -- 航段类型 (R=右转, L=左转)
    min_altitude INTEGER NOT NULL,                    -- 最低等待高度 (英尺)
    max_altitude INTEGER NOT NULL,                    -- 最高等待高度 (英尺)
    speed_limit INTEGER NOT NULL,                     -- 速度限制 (节)
    
    KEY idx_holdings_waypoint (waypoint_name),
    KEY idx_holdings_airport (airport_icao),
    KEY idx_holdings_region (region_code)
);
"""

NAVAIDS_TABLE = """
DROP TABLE IF EXISTS navaids;
CREATE TABLE navaids (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nav_type INTEGER NOT NULL,                        -- 导航设备类型 (3=VOR, 12=DME等，和finix的一样)
    latitude DECIMAL(12, 9) NOT NULL,                 -- 纬度
    longitude DECIMAL(12, 9) NOT NULL,                -- 经度
    elevation INTEGER NOT NULL,                       -- 海拔高度 (英尺)
    frequency INTEGER NOT NULL,                       -- 频率 (kHz)
    range_nm INTEGER NOT NULL,                        -- 作用距离 (海里)
    magnetic_variation DECIMAL(12, 3) NOT NULL,       -- 磁偏角/方位角 (某些类型存储编码方位角)
    identifier VARCHAR(16) NOT NULL,                  -- 导航台标识符 (最长9字符)
    usage_type VARCHAR(4) NOT NULL,                   -- 使用类型 (ENRT=航路等)
    region_code VARCHAR(2) NOT NULL,                  -- 地区代码
    name VARCHAR(100) NOT NULL,                       -- 导航台名称 (可能包含长描述)
    
    KEY idx_navaids_identifier (identifier),
    KEY idx_navaids_type (nav_type),
    KEY idx_navaids_region (region_code),
    KEY idx_navaids_location (latitude, longitude),
    KEY idx_navaids_frequency (frequency)
);
"""

## 这个和finix的db又不一样，它是直接保留并截断的整数部分，而且从西经开始算，而之前mapbox是从东经开始算
MORA_TABLE = """
DROP TABLE IF EXISTS mora;
CREATE TABLE mora (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    latitude_deg INTEGER NOT NULL,                    -- 纬度 (整数部分)
    longitude_deg INTEGER NOT NULL,                   -- 经度 (整数部分)
    grid_data TEXT NOT NULL,                          -- 网格高度数据 (30个值的字符串)
    
    KEY idx_mora_location (latitude_deg, longitude_deg)
);
"""

MSA_TABLE = """
DROP TABLE IF EXISTS msa;
CREATE TABLE msa (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    sector_count INTEGER NOT NULL,                    -- 扇区数量 (1-3)
    navaid_identifier VARCHAR(16) NOT NULL,            -- 导航台标识符
    region_code VARCHAR(2) NOT NULL,                  -- 地区代码
    airport_icao VARCHAR(4) NOT NULL,                 -- 机场ICAO代码
    msa_type CHAR(1) NOT NULL,                        -- MSA类型 (M=MSA)
    
    -- 扇区1数据
    sector1_bearing INTEGER,                          -- 扇区1方位角
    sector1_altitude INTEGER,                         -- 扇区1高度
    sector1_radius INTEGER,                           -- 扇区1半径
    
    -- 扇区2数据
    sector2_bearing INTEGER,
    sector2_altitude INTEGER,
    sector2_radius INTEGER,
    
    -- 扇区3数据
    sector3_bearing INTEGER,
    sector3_altitude INTEGER,
    sector3_radius INTEGER,
    
    KEY idx_msa_navaid (navaid_identifier),
    KEY idx_msa_airport (airport_icao),
    KEY idx_msa_region (region_code)
);
"""

# 复杂，按AIRAC转的，不保证完全对，terminal的后面再改
TERMINAL_PROCEDURES_TABLE = """
DROP TABLE IF EXISTS terminal_procedures;
CREATE TABLE terminal_procedures (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    airport_icao VARCHAR(4) NOT NULL,                 -- 机场ICAO代码
    procedure_type VARCHAR(10) NOT NULL,              -- 程序类型 (STAR, SID, APPCH等)
    sequence_number VARCHAR(10) NOT NULL,             -- 序列号
    route_type INTEGER NOT NULL,                      -- 航路类型
    procedure_name VARCHAR(20) NOT NULL,              -- 程序名称
    transition_name VARCHAR(20),                      -- 过渡段名称
    waypoint_name VARCHAR(5) NOT NULL,                -- 航路点名称
    waypoint_region VARCHAR(16) NOT NULL,              -- 航路点地区代码
    waypoint_section INTEGER NOT NULL,                -- 航路点段落代码
    waypoint_type VARCHAR(16) NOT NULL,                -- 航路点类型
    waypoint_description VARCHAR(10),                 -- 航路点描述
    path_terminator VARCHAR(16) NOT NULL,              -- 航径终止符
    
    -- 参考导航台信息
    ref_navaid_identifier VARCHAR(6),                 -- 参考导航台标识符
    ref_navaid_region VARCHAR(16),                     -- 参考导航台地区代码
    ref_navaid_section INTEGER,                       -- 参考导航台段落代码
    ref_navaid_type VARCHAR(16),                      -- 参考导航台类型
    
    -- 坐标和距离信息
    theta DECIMAL(6, 1),                              -- 方位角
    rho DECIMAL(6, 2),                                -- 距离
    magnetic_course DECIMAL(6, 1),                    -- 磁航向
    distance_time VARCHAR(4),                         -- 距离或时间
    
    -- 高度限制
    altitude_description VARCHAR(16),                     -- 高度描述符
    altitude1 VARCHAR(10),                            -- 高度1
    altitude2 VARCHAR(10),                            -- 高度2
    transition_altitude VARCHAR(10),                  -- 过渡高度
    
    -- 速度限制
    speed_limit VARCHAR(10),                          -- 速度限制
    
    -- 其他参数
    vertical_angle DECIMAL(4, 1),                     -- 垂直角度
    center_fix VARCHAR(5),                            -- 中心定位点
    multiple_code VARCHAR(16),                        -- 多重代码
    gnss_fms_indication VARCHAR(16),                      -- GNSS/FMS指示
    
    KEY idx_terminal_airport (airport_icao),
    KEY idx_terminal_type (procedure_type),
    KEY idx_terminal_name (procedure_name),
    KEY idx_terminal_waypoint (waypoint_name),
    KEY idx_terminal_sequence (airport_icao, procedure_type, procedure_name, sequence_number)
);
"""

ALL_TABLES = {
    'airports': AIRPORTS_TABLE,
    'airways': AIRWAYS_TABLE,
    'waypoints': WAYPOINTS_TABLE,
    'holdings': HOLDINGS_TABLE,
    'navaids': NAVAIDS_TABLE,
    'mora': MORA_TABLE,
    'msa': MSA_TABLE,
    'terminal_procedures': TERMINAL_PROCEDURES_TABLE
}

def get_create_database_sql():
    sql_statements = []

    # 添加所有表的创建语句
    for table_name, create_sql in ALL_TABLES.items():
        sql_statements.append(f"-- {table_name.upper()} 表")
        sql_statements.append(create_sql)
        sql_statements.append("")
    
    return "\n".join(sql_statements)

if __name__ == "__main__":
    print(get_create_database_sql())
