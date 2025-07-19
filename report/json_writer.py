"""JSON writer for saving extracted data to JSON files.

这个模块提供了专门的JSON写入器，用于将从XML报告中提取的数据保存为JSON格式。
支持多种输出格式，包括标准数据数组和个人档案格式。

主要功能：
- 标准JSON数据数组输出（适用于数据分析）
- 个人档案JSON输出（结构化格式，适用于报告展示）
- 自动文件名生成（基于时间戳或用户信息）
- 文件名清理和验证
- UTF-8编码支持
- 灵活的输出目录管理
- 美化的JSON格式输出

支持的输出格式：
1. 标准格式：JSON数组，每个元素为一条记录
2. 档案格式：结构化JSON对象，按类别分组

使用示例：
    writer = JSONWriter('output_dir')
    writer.write_data(data_list, 'report.json')
    writer.write_individual_profile(profile_data)
"""

import json
import os
import base64
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from collections import OrderedDict

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # 使用非交互式后端
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Chart generation will be disabled.")


class JSONWriter:
    """JSON文件写入器。
    
    这个类负责将提取的数据保存为JSON格式文件。提供了多种输出格式和
    自动化的文件管理功能，确保数据能够正确保存并便于后续处理。
    
    Attributes:
        output_dir (Path): 输出目录路径，所有JSON文件将保存在此目录中
    
    Features:
        - 自动创建输出目录
        - UTF-8编码支持
        - 文件名自动清理和验证
        - 多种输出格式支持
        - 美化的JSON格式输出
        - 错误处理和验证
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """初始化JSON写入器。
        
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
        """将数据写入JSON文件（标准数组格式）。
        
        将数据列表写入JSON文件，保存为JSON数组格式。
        适用于数据分析和批量处理场景。
        
        Args:
            data_list (List[Dict[str, Any]]): 要写入的数据列表，每个字典代表一条记录。
            filename (str, optional): 输出JSON文件名，可以包含或不包含.json扩展名。
                如果为None，将基于时间戳自动生成文件名。
                
        Returns:
            str: 创建的JSON文件的完整路径。
            
        Raises:
            ValueError: 当数据列表为空时抛出。
            OSError: 当文件写入失败时抛出。
            
        Note:
            - 使用UTF-8编码
            - 如果文件已存在，将被覆盖
            - 输出美化的JSON格式（缩进为2个空格）
        """
        if not data_list:
            raise ValueError("No data to write")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_data_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        output_path = self.output_dir / filename
        
        # Convert OrderedDict to regular dict for JSON serialization and process curve data
        json_data = []
        for item in data_list:
            if isinstance(item, OrderedDict):
                processed_item = dict(item)
            else:
                processed_item = item.copy()
            
            # 处理心态分布曲线数据，生成柱状图base64
            if 'distribution_curve_data' in processed_item:
                curve_data_str = processed_item.get('distribution_curve_data', '[]')# 获取基准曲线数据
                base_curve_data_str = item.get('base_curve_data', '[]')
                
                # 生成图表数据（包含基准曲线对比）
                chart_base64 = self._generate_chart_base64(curve_data_str, base_curve_data_str)
                if chart_base64:
                    processed_item['distribution_curve_chart'] = chart_base64
                # 移除原始曲线数据字符串，只保留base64图表
                del processed_item['distribution_curve_data']
            
            json_data.append(processed_item)
        
        # Write to JSON
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def write_individual_profile(self, data: Dict[str, Any], filename: str = None) -> str:
        """将个人档案数据写入JSON文件（结构化格式）。
        
        将单个用户的档案数据写入JSON文件，采用结构化格式，
        按数据类别分组显示。适用于个人报告和档案展示场景。
        
        Args:
            data (Dict[str, Any]): 包含个人档案数据的字典。
                支持嵌套字典结构，会自动按类别分组显示。
            filename (str, optional): 输出JSON文件名。
                如果为None，将基于用户信息（姓名、时间戳）自动生成文件名。
                
        Returns:
            str: 创建的JSON文件的完整路径。
            
        Raises:
            ValueError: 当数据字典为空时抛出。
            OSError: 当文件写入失败时抛出。
            
        Note:
            - 输出结构化的JSON格式，按类别分组
            - 使用UTF-8编码
            - 自动生成的文件名格式：'profile_用户名_时间戳.json'
        """
        if not data:
            raise ValueError("No data to write")
        
        # Generate filename based on user info if not provided
        if filename is None:
            user_name = data.get('name', 'unknown')
            user_uuid = data.get('uuid', 'unknown')
            date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
            filename = f"profile_{user_name}_{user_uuid}_{date}.json"
        
        # Clean filename (remove invalid characters)
        filename = self._clean_filename(filename)
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        output_path = self.output_dir / filename
        
        # Structure profile data by categories
        structured_data = {
            "user_information": {},
            "brain_fatigue": {},
            "psycho_physiological_state": {},
            "mind_distribution": {},
            "curve_data": {},
            "metadata": {}
        }
        
        # Categorize data
        user_fields = ['uuid', 'name', 'gender', 'age', 'company', 'site', 'date', 'profile_id']
        brain_fields = ['brain_fatigue_state', 'brain_fatigue_level', 'emotion', 'energy']
        curve_fields = [k for k in data.keys() if k.startswith(('distribution_curve', 'curve_'))]
        mind_fields = [k for k in data.keys() if k.startswith('mind_distribution') or k.startswith('distribution')]
        metadata_fields = ['source_file', 'processed_time', 'test_date']
        
        # Populate categories
        for field in user_fields:
            if field in data:
                structured_data["user_information"][field] = data[field]
        
        for field in brain_fields:
            if field in data:
                structured_data["brain_fatigue"][field] = data[field]
        
        for field in curve_fields:
            if field in data:
                structured_data["curve_data"][field] = data[field]
        
        for field in mind_fields:
            if field in data:
                structured_data["mind_distribution"][field] = data[field]
        
        for field in metadata_fields:
            if field in data:
                structured_data["metadata"][field] = data[field]
        
        # Add emotional variation and psychological dimensions
        emotional_fields = [k for k in data.keys() if k.startswith('emotional_variation')]
        psycho_fields = [k for k in data.keys() if any(k.startswith(prefix) for prefix in 
                        ['攻击性', '压力', '不安', '怀疑', '平衡', '自信', '能量', '自我调节', '抑制', '神经质', '抑郁', '幸福', 
                         '专注', '放松', '愉悦', '疲劳', '紧张'])]
        
        for field in emotional_fields + psycho_fields:
            if field in data:
                structured_data["psycho_physiological_state"][field] = data[field]
        
        # Convert OrderedDict to regular dict for JSON serialization
        if isinstance(data, OrderedDict):
            data = dict(data)
        
        # Write to JSON
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(structured_data, jsonfile, ensure_ascii=False, indent=2)
        
        return str(output_path)
    
    def _generate_chart_base64(self, curve_data_str: str, base_curve_data_str: str = None) -> Optional[str]:
        """生成心态分布曲线的柱状图base64数据，包含基准曲线对比。
        
        Args:
            curve_data_str (str): 心态分布曲线数据字符串，格式如 '[{id:pt0,x:0.1,y:0.5},...}]'
            base_curve_data_str (str, optional): 基准曲线数据字符串，格式相同
            
        Returns:
            Optional[str]: 柱状图的base64编码字符串，如果生成失败则返回None
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        try:
            # 解析曲线数据字符串
            if not curve_data_str or curve_data_str == '[]':
                return None
                
            # 简单解析数据字符串（格式：[{id:pt0,x:0.1,y:0.5},...}]）
            curve_data_str = curve_data_str.strip('[]')
            if not curve_data_str:
                return None
                
            points = []
            # 分割每个点的数据
            point_strs = curve_data_str.split('},{')
            for i, point_str in enumerate(point_strs):
                # 清理字符串
                point_str = point_str.strip('{}').replace('{', '').replace('}', '')
                
                # 解析x和y值
                x_val, y_val = None, None
                parts = point_str.split(',')
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'x':
                            try:
                                x_val = float(value)
                            except ValueError:
                                continue
                        elif key == 'y':
                            try:
                                y_val = float(value)
                            except ValueError:
                                continue
                
                if x_val is not None and y_val is not None:
                    points.append((x_val, y_val))
            
            if not points:
                return None
                
            # 按x值排序
            points.sort(key=lambda p: p[0])
            
            # 解析基准曲线数据
            base_points = []
            if base_curve_data_str and base_curve_data_str != '[]':
                try:
                    base_curve_data_str = base_curve_data_str.strip('[]')
                    if base_curve_data_str:
                        base_point_strs = base_curve_data_str.split('},{')
                        for i, point_str in enumerate(base_point_strs):
                            point_str = point_str.strip('{}').replace('{', '').replace('}', '')
                            x_val, y_val = None, None
                            parts = point_str.split(',')
                            for part in parts:
                                if ':' in part:
                                    key, value = part.split(':', 1)
                                    key = key.strip()
                                    value = value.strip()
                                    if key == 'x':
                                        try:
                                            x_val = float(value)
                                        except ValueError:
                                            continue
                                    elif key == 'y':
                                        try:
                                            y_val = float(value)
                                        except ValueError:
                                            continue
                            
                            if x_val is not None and y_val is not None:
                                base_points.append((x_val, y_val))
                        
                        # 按x值排序
                        base_points.sort(key=lambda p: p[0])
                except Exception as e:
                    print(f"Error parsing base curve data: {e}")
                    base_points = []
            
            # 创建柱状图
            fig, ax = plt.subplots(figsize=(12, 8))
            x_values = [p[0] for p in points]
            y_values = [p[1] for p in points]
            
            # 绘制心态分布曲线柱状图
            bars = ax.bar(x_values, y_values, width=0.02, alpha=0.7, color='steelblue', 
                         edgecolor='navy', linewidth=0.5, label='实际心态分布')
            
            # 绘制基准曲线（如果有数据）
            if base_points:
                base_x_values = [p[0] for p in base_points]
                base_y_values = [p[1] for p in base_points]
                ax.plot(base_x_values, base_y_values, color='red', linewidth=2, 
                       alpha=0.8, label='标准正态分布基准线')
            
            # 设置图表样式
            ax.set_xlabel('X值', fontsize=12)
            ax.set_ylabel('Y值', fontsize=12)
            ax.set_title('心态分布曲线对比图', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 调整布局
            plt.tight_layout()
            
            # 保存为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # 转换为base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 清理资源
            plt.close(fig)
            buffer.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除无效字符。
        
        Args:
            filename (str): 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # Remove invalid characters for Windows/Unix filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        return filename