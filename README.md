# X-Plane-to-SQL-and-AIRAC424

Concurrently convert X-Plane’s navigation data (including airports, airways, navigational aids, and fixes) to SQL format. Additionally, convert CIFP data to AIRAC424 format.

将X-Plane导航数据转换为SQL格式的工具。支持机场、航路、航路点、等待航线、导航设备、MORA、MSA和终端程序数据的完整转换。

## 已实现的功能特性

- **机场数据解析** - 解析 `earth_aptmeta.dat` 文件，包含机场基本信息、跑道数据等
- **航路数据解析** - 解析 `earth_awy.dat` 文件，包含航路网络和连接信息
- **航路点数据解析** - 解析 `earth_fix.dat` 文件，支持终端/航路点分类
- **等待航线解析** - 解析 `earth_hold.dat` 文件，包含等待程序数据
- **导航设备解析** - 解析 `earth_nav.dat` 文件，支持VOR、DME、NDB等设备
- **MORA数据解析** - 解析 `earth_mora.dat` 文件，最低安全高度网格数据
- **MSA数据解析** - 解析 `earth_msa.dat` 文件，最低扇区高度数据
- **终端程序解析** - 解析 `CIFP/*.dat` 文件，AIRAC424格式的SID/STAR/进近程序
- **SQL生成** - 生成完整的MySQL兼容SQL文件，包含表结构和数据
- **数据验证** - 内置数据验证和错误处理机制
- **模块化设计** - 易于维护和扩展

## 安装和使用

### 1. 环境要求

- Python 3.7+

### 2. 数据准备

将X-Plane的导航数据数据文件放置在 `source/` 目录下：

```bash
source/
├── earth_aptmeta.dat
├── earth_apt.dat
├── earth_awy.dat
├── earth_fix.dat
├── earth_hold.dat
├── earth_nav.dat
├── earth_mora.dat
├── earth_msa.dat
└── CIFP/
    ├── KORD.dat
    └── ...
```

### 3. 基本使用

```bash
# 转换所有数据
cd src
python main.py

# 指定源目录和输出文件
python main.py -s /path/to/source -o /path/to/output.sql

# 只转换特定表
python main.py -t airports,waypoints,airways

# 启用详细输出
python main.py -v
```

### 4. 命令行参数

- `-s, --source DIR` - 源数据目录路径
- `-o, --output FILE` - 输出SQL文件路径
- `-t, --tables LIST` - 指定要处理的表 (逗号分隔)
- `-v, --verbose` - 详细输出模式
- `-h, --help` - 显示帮助信息

### 5. 可选表名

- `airports` - 机场数据
- `airways` - 航路数据
- `waypoints` - 航路点数据
- `holdings` - 等待航线数据
- `navaids` - 导航设备数据
- `mora` - MORA数据
- `msa` - MSA数据
- `terminal_procedures` - 终端程序数据

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 更新日志

### v1.0.0 (2025-09-28)

- 完成所有数据类型的解析器实现
- 实现完整的SQL生成功能
- 添加数据验证和错误处理
- 支持命令行参数和配置选项
- 完善的文档和使用说明

**todo**

CIFP与AIRAC424的校验还未完成，因为格式过于复杂，后续会逐步校验
