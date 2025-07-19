"""Report module for parsing XML files and extracting data.

这个模块提供了完整的XML报告文件处理功能，包括：
- XML文件解析（支持无根节点的XML文件）
- 数据提取（用户信息、脑疲劳数据、心理生理状态、心态分布等）
- CSV文件输出（个人档案和汇总数据）
- 心态分布曲线数据提取

主要组件：
- XMLReportParser: XML文件解析器
- DataExtractor: 数据提取器
- CSVWriter: CSV文件写入器
- ReportProcessor: 主要处理器（在processor模块中）

使用示例：
    from report.processor import ReportProcessor
    
    processor = ReportProcessor('reportFile', 'output')
    results = processor.process_all_files()
"""

from .parser import XMLReportParser
from .extractor import DataExtractor
from .csv_writer import CSVWriter
from .processor import ReportProcessor

__all__ = [
    'XMLReportParser',
    'DataExtractor', 
    'CSVWriter',
    'ReportProcessor'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'ChatEcho Team'
__description__ = 'XML报告文件解析和数据提取模块'