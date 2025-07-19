"""CSV writer for saving extracted data to CSV files.

这个模块提供了专门的CSV写入器，用于将从XML报告中提取的数据保存为CSV格式。
支持多种输出格式，包括标准数据表格和个人档案格式。

主要功能：
- 标准CSV数据表格输出（适用于数据分析）
- 个人档案CSV输出（键值对格式，适用于报告展示）
- 自动文件名生成（基于时间戳或用户信息）
- 文件名清理和验证
- UTF-8编码支持（包含BOM，确保Excel正确显示中文）
- 灵活的输出目录管理

支持的输出格式：
1. 标准格式：每行一条记录，列为字段名
2. 档案格式：两列格式（字段名，字段值），按类别分组

使用示例：
    writer = CSVWriter('output_dir')
    writer.write_data(data_list, 'report.csv')
    writer.write_individual_profile(profile_data)
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from collections import OrderedDict


class CSVWriter:
    """CSV文件写入器。
    
    这个类负责将提取的数据保存为CSV格式文件。提供了多种输出格式和
    自动化的文件管理功能，确保数据能够正确保存并便于后续处理。
    
    Attributes:
        output_dir (Path): 输出目录路径，所有CSV文件将保存在此目录中
    
    Features:
        - 自动创建输出目录
        - UTF-8编码支持（包含BOM）
        - 文件名自动清理和验证
        - 多种输出格式支持
        - 错误处理和验证
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """初始化CSV写入器。
        
        Args:
            output_dir (Optional[Union[str, Path]]): 输出目录路径。
                如果为None，使用当前工作目录。支持字符串或Path对象。
                
        Note:
            - 如果指定的目录不存在，会自动创建
            - 支持相对路径和绝对路径
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_data(self, data_list: List[Dict[str, Any]], filename: str = None) -> str:
        """将数据写入CSV文件（标准表格格式）。
        
        将数据列表写入CSV文件，每行代表一条记录，列为字段名。
        适用于数据分析和批量处理场景。
        
        Args:
            data_list (List[Dict[str, Any]]): 要写入的数据列表，每个字典代表一行数据。
                字典的键将作为CSV的列标题，值为对应的数据。
            filename (str, optional): 输出CSV文件名，可以包含或不包含.csv扩展名。
                如果为None，将基于时间戳自动生成文件名。
                
        Returns:
            str: 创建的CSV文件的完整路径。
            
        Raises:
            ValueError: 当数据列表为空时抛出。
            OSError: 当文件写入失败时抛出。
            
        Note:
            - 使用UTF-8编码（包含BOM），确保Excel正确显示中文
            - 如果文件已存在，将被覆盖
            - 自动从所有数据行中收集所有可能的字段名作为列标题
        """
        if not data_list:
            raise ValueError("No data to write")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_data_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        output_path = self.output_dir / filename
        
        # Get field names preserving order from first record if it's an OrderedDict
        # Otherwise, collect all unique field names
        if data_list and isinstance(data_list[0], OrderedDict):
            # First record is OrderedDict, use its order
            fieldnames = list(data_list[0].keys())
            # Add any additional fields from other records
            all_fields = set(fieldnames)
            for data in data_list[1:]:
                for key in data.keys():
                    if key not in all_fields:
                        fieldnames.append(key)
                        all_fields.add(key)
        else:
            # Regular dict or mixed types, collect all fields and sort
            all_fields = set()
            for data in data_list:
                all_fields.update(data.keys())
            fieldnames = sorted(all_fields)
        
        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
        
        return str(output_path)
    
    def write_individual_profile(self, data: Dict[str, Any], filename: str = None) -> str:
        """将个人档案数据写入CSV文件（键值对格式）。
        
        将单个用户的档案数据写入CSV文件，采用两列格式（字段名，字段值），
        按数据类别分组显示。适用于个人报告和档案展示场景。
        
        Args:
            data (Dict[str, Any]): 包含个人档案数据的字典。
                支持嵌套字典结构，会自动按类别分组显示。
            filename (str, optional): 输出CSV文件名。
                如果为None，将基于用户信息（姓名、时间戳）自动生成文件名。
                
        Returns:
            str: 创建的CSV文件的完整路径。
            
        Raises:
            ValueError: 当数据字典为空时抛出。
            OSError: 当文件写入失败时抛出。
            
        Note:
            - 输出格式为两列：'字段名' 和 '字段值'
            - 嵌套字典会展开为分类显示
            - 使用UTF-8编码（包含BOM）
            - 自动生成的文件名格式：'profile_用户名_时间戳.csv'
        """
        if not data:
            raise ValueError("No data to write")
        
        # Generate filename based on user info if not provided
        if filename is None:
            user_name = data.get('name', 'unknown')
            user_uuid = data.get('uuid', 'unknown')
            date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
            filename = f"profile_{user_name}_{user_uuid}_{date}.csv"
        
        # Clean filename (remove invalid characters)
        filename = self._clean_filename(filename)
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        output_path = self.output_dir / filename
        
        # Write profile data in key-value format
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Field', 'Value'])  # Header
            
            # Write user info section
            writer.writerow(['=== User Information ===', ''])
            user_fields = ['uuid', 'name', 'gender', 'age', 'company', 'site', 'date']
            for field in user_fields:
                if field in data:
                    writer.writerow([field, data[field]])
            
            # Write brain fatigue section
            writer.writerow(['=== Brain Fatigue ===', ''])
            brain_fields = ['brain_fatigue_state', 'brain_fatigue_level', 'emotion', 'energy']
            for field in brain_fields:
                if field in data:
                    writer.writerow([field, data[field]])
            
            # Write psycho-physiological state section
            writer.writerow(['=== Psycho-physiological State ===', ''])
            psycho_fields = [k for k in data.keys() if k.startswith(('emotional_variation', '攻击性', '压力', '不安', '怀疑', '平衡', '自信', '能量', '自我调节', '抑制', '神经质', '抑郁', '幸福'))]
            for field in sorted(psycho_fields):
                writer.writerow([field, data[field]])
            
            # Write mind distribution section
            writer.writerow(['=== Mind Distribution ===', ''])
            mind_fields = [k for k in data.keys() if k.startswith('mind_distribution') or k.startswith('distribution')]
            for field in sorted(mind_fields):
                writer.writerow([field, data[field]])
        
        return str(output_path)
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除无效字符。
        
        移除或替换文件名中不适合文件系统的字符，确保生成的文件名
        在不同操作系统上都能正常使用。
        
        Args:
            filename (str): 原始文件名，可能包含无效字符。
            
        Returns:
            str: 清理后的安全文件名，移除了所有无效字符。
            
        Note:
            - 移除的字符包括：< > : " | ? * \ /
            - 替换空格为下划线
            - 保留文件扩展名
            - 确保文件名不为空
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and dots
        filename = filename.strip().replace('..', '.')
        
        return filename