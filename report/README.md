# Report Module

报告解析模块，用于解析XML格式的心理生理状态报告文件并生成CSV格式的个人档案。

## 功能特性

- **XML解析**: 自动处理没有根节点的XML文件
- **数据提取**: 提取用户信息、脑疲劳状态、心理生理状态和心态分布数据
- **曲线数据提取**: 专门提取心态分布曲线（DistributionCurve）的完整坐标点数据
- **CSV输出**: 生成个人档案CSV、合并数据CSV和曲线数据CSV文件
- **批量处理**: 支持批量处理多个XML文件

## 模块结构

```
report/
├── __init__.py          # 模块初始化
├── parser.py            # XML解析器
├── extractor.py         # 数据提取器
├── csv_writer.py        # CSV写入器
├── processor.py         # 主处理器
├── example.py           # 使用示例
└── README.md           # 说明文档
```

## 提取的数据字段

### 用户信息 (UserInfo)
- uuid: 用户唯一标识
- name: 姓名
- gender: 性别
- age: 年龄
- company: 公司/机构
- site: 部门/院系
- date: 检测日期

### 脑疲劳状态 (BrainFatigue)
- brain_fatigue_state: 脑疲劳状态 (如: "健康")
- brain_fatigue_level: 脑疲劳度 (数值)
- emotion: 情绪 (数值)
- energy: 能量 (数值)

### 心理生理状态 (Psycho-physiologicalState)
- emotional_variation_*: 情绪变化相关数据
- 各种心理因子的统计数据:
  - 攻击性、压力、不安、怀疑、平衡、自信
  - 能量、自我调节、抑制、神经质、抑郁、幸福
  - 每个因子包含: range_min, range_max, min, average, max, judge

### 心态分布 (MindDistribution)
- mind_distribution_title: 心态分布标题
- distribution_curve_title: 分布曲线标题
- distribution_points_count: 分布点数量
- sample_distribution_points: 样本分布点

## 使用方法

### 1. 基本使用

```python
from report.processor import ReportProcessor

# 创建处理器
processor = ReportProcessor(
    report_dir='./reportFile',    # XML文件目录
    output_dir='./report_output'  # 输出目录
)

# 处理所有文件
results = processor.process_all_files()
print(f"处理了 {results['processed_files']} 个文件")
```

### 2. 处理单个文件

```python
from report.processor import ReportProcessor

processor = ReportProcessor('./reportFile', './output')
data = processor.process_single_file('./reportFile/example.xml')

if data:
    print(f"用户: {data['name']}")
    print(f"脑疲劳状态: {data['brain_fatigue_state']}")
    print(f"情绪: {data['emotion']}")
```

### 3. 提取心态分布曲线数据

```python
from report.processor import ReportProcessor

# 提取所有文件的DistributionCurve数据
processor = ReportProcessor("d:/PythonProject/ChatEcho/reportFile", "d:/PythonProject/ChatEcho/curve_output")
results = processor.save_distribution_curves()
print(f"成功提取 {results['processed_files']} 个文件的曲线数据")

# 提取单个文件的曲线数据
curve_data = processor.extract_distribution_curve("path/to/file.xml")
print(f"提取到 {len(curve_data)} 个数据点")
for point in curve_data[:5]:  # 显示前5个点
    print(f"点{point['point_id']}: x={point['x']}, y={point['y']}")
```

### 3. 命令行使用

```bash
# 处理指定目录的所有XML文件
python -m report.processor ./reportFile ./output

# 或者运行测试脚本
python test_report.py
```

### 4. 运行示例

```python
from report.example import run_example

# 运行示例处理
run_example()
```

## 输出文件

### 个人档案CSV (profile_*.csv)
- 格式: 字段-值对
- 按类别分组显示数据
- 适合查看单个用户的完整档案

### 合并数据CSV (combined_report_data.csv)
- 格式: 表格形式
- 所有用户数据在一个文件中
- 适合数据分析和统计

### 心态分布曲线数据CSV (distribution_curve_*.csv)
- 格式: 表格形式
- 包含心态分布曲线的完整坐标点数据
- 字段包括: point_id, x, y
- 每个XML文件生成对应的曲线数据文件
- 适合进行曲线分析和可视化

## 错误处理

模块包含完善的错误处理机制:
- XML解析错误处理
- 文件不存在处理
- 数据提取异常处理
- 详细的错误日志输出

## 依赖要求

- Python 3.6+
- xml.etree.ElementTree (标准库)
- pathlib (标准库)
- csv (标准库)

## 注意事项

1. **XML格式**: 模块专门处理没有根节点的XML文件，会自动添加根节点包装
2. **编码**: 输出CSV文件使用UTF-8-BOM编码，确保中文正确显示
3. **文件名**: 自动清理文件名中的非法字符
4. **内存使用**: 适合处理中等规模的XML文件，大文件可能需要优化

## 示例输出

```
Testing Report Module
==============================
Report directory: D:\PythonProject\ChatEcho\reportFile
Found 1 XML files:
  - 2025-07-16 15_36_00_result.xml

Processing: 2025-07-16 15_36_00_result.xml
Created individual profile: profile_2025-07-16 15_36_00_result.csv

Processing Summary:
Total files found: 1
Successfully processed: 1
Failed to process: 0
Output files created: 2

Generated CSV files:
  - profile_2025-07-16 15_36_00_result.csv (2165 bytes)
  - combined_report_data.csv (2025 bytes)
```

## 扩展功能

模块设计为可扩展的，可以轻松添加:
- 新的数据提取字段
- 不同的输出格式
- 数据验证和清洗
- 统计分析功能