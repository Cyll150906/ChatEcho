"""主处理器模块，用于处理XML报告并生成CSV输出。

这个模块是整个报告处理系统的核心，提供了完整的XML报告处理流程，
从文件解析到数据提取，再到CSV输出的一站式解决方案。

主要功能：
- 批量处理XML报告文件
- 单个文件处理和数据提取
- 心态分布曲线数据专项提取
- 多种格式的CSV输出
- 处理结果统计和汇总
- 错误处理和日志记录

支持的数据类型：
- 用户基本信息（姓名、UUID、时间戳等）
- 脑疲劳状态数据
- 心理生理状态数据
- 心态分布统计数据
- 心态分布曲线详细数据（256个数据点）

输出格式：
- 标准CSV数据表格（适用于数据分析）
- 个人档案CSV（适用于报告展示）
- 心态分布曲线CSV（适用于可视化分析）

使用示例：
    processor = ReportProcessor('input_dir', 'output_dir')
    results = processor.process_all_files()
    processor.save_distribution_curves()
    stats = processor.get_summary_statistics(results)
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
from collections import OrderedDict

from .parser import XMLReportParser
from .extractor import DataExtractor
from .json_writer import JSONWriter


class ReportProcessor:
    """Main processor for handling XML report files and generating CSV output."""
    
    def __init__(self, report_dir: str, output_dir: str = None):
        """Initialize report processor.
        
        Args:
            report_dir: Directory containing XML report files
            output_dir: Output directory for CSV files. If None, creates 'output' subdirectory.
        """
        self.report_dir = Path(report_dir)
        if not self.report_dir.exists():
            raise FileNotFoundError(f"Report directory not found: {report_dir}")
        
        # Set output directory
        if output_dir is None:
            self.output_dir = self.report_dir.parent / 'report_output'
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.parser = XMLReportParser()
        self.json_writer = JSONWriter(str(self.output_dir))
    
    def process_all_files(self) -> Dict[str, Any]:
        """Process all XML files in the report directory.
        
        Returns:
            Dictionary containing processing results and statistics
        """
        xml_files = list(self.report_dir.glob('*.xml'))
        
        if not xml_files:
            print(f"No XML files found in {self.report_dir}")
            return {'processed_files': 0, 'failed_files': 0, 'output_files': []}
        
        print(f"Found {len(xml_files)} XML files to process")
        
        all_data = []
        processed_files = 0
        failed_files = 0
        output_files = []
        
        for xml_file in xml_files:
            print(f"Processing: {xml_file.name}")
            
            try:
                # Parse XML file
                root = self.parser.parse_file(str(xml_file))
                if root is None:
                    print(f"Failed to parse {xml_file.name}")
                    failed_files += 1
                    continue
                
                # Extract data
                extractor = DataExtractor(root)
                data = extractor.extract_all_data()
                
                # Add source file info
                data['source_file'] = xml_file.name
                data['processed_time'] = str(Path(xml_file).stat().st_mtime)
                
                all_data.append(data)
                
                # Create individual profile CSV
                try:
                    profile_file = self.csv_writer.write_individual_profile(
                        data, 
                        f"profile_{xml_file.stem}"
                    )
                    output_files.append(profile_file)
                    print(f"Created individual profile: {Path(profile_file).name}")
                except Exception as e:
                    print(f"Failed to create individual profile for {xml_file.name}: {e}")
                
                processed_files += 1
                
            except Exception as e:
                print(f"Error processing {xml_file.name}: {e}")
                failed_files += 1
        
        # Create combined CSV with all data
        if all_data:
            try:
                combined_file = self.csv_writer.write_data(all_data, 'combined_report_data')
                output_files.append(combined_file)
                print(f"Created combined report: {Path(combined_file).name}")
            except Exception as e:
                print(f"Failed to create combined report: {e}")
        
        # Print summary
        print(f"\nProcessing Summary:")
        print(f"Total files found: {len(xml_files)}")
        print(f"Successfully processed: {processed_files}")
        print(f"Failed to process: {failed_files}")
        print(f"Output files created: {len(output_files)}")
        print(f"Output directory: {self.output_dir}")
        
        return {
            'total_files': len(xml_files),
            'processed_files': processed_files,
            'failed_files': failed_files,
            'output_files': output_files,
            'output_directory': str(self.output_dir)
        }
    
    def process_single_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process a single XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            Extracted data dictionary or None if processing failed
        """
        try:
            # Parse XML file
            root = self.parser.parse_file(file_path)
            if root is None:
                return None
            
            # Extract data
            extractor = DataExtractor(root)
            data = extractor.extract_all_data()
            
            # Add source file info
            file_path_obj = Path(file_path)
            data['source_file'] = file_path_obj.name
            data['processed_time'] = str(file_path_obj.stat().st_mtime)
            
            return data
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def extract_distribution_curve(self, file_path: str) -> Optional[List[Dict[str, str]]]:
        """Extract DistributionCurve data from a single XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            List of curve points or None if extraction failed
        """
        try:
            # Parse XML file
            root = self.parser.parse_file(file_path)
            if root is None:
                return None
            
            # Extract distribution curve data
            extractor = DataExtractor(root)
            curve_data = extractor.extract_distribution_curve_data()
            
            return curve_data
            
        except Exception as e:
            print(f"Error extracting distribution curve from {file_path}: {e}")
            return None
    
    def save_distribution_curves(self) -> Dict[str, Any]:
        """Extract and save DistributionCurve data from all XML files.
        
        Returns:
            Dictionary containing processing results
        """
        xml_files = list(self.report_dir.glob('*.xml'))
        
        if not xml_files:
            print(f"No XML files found in {self.report_dir}")
            return {'processed_files': 0, 'failed_files': 0, 'output_files': []}
        
        print(f"Extracting DistributionCurve data from {len(xml_files)} XML files")
        
        processed_files = 0
        failed_files = 0
        output_files = []
        
        for xml_file in xml_files:
            print(f"Processing curve data from: {xml_file.name}")
            
            try:
                # Extract distribution curve data
                curve_data = self.extract_distribution_curve(str(xml_file))
                
                if curve_data is None or not curve_data:
                    print(f"No distribution curve data found in {xml_file.name}")
                    failed_files += 1
                    continue
                
                # Save curve data to CSV
                curve_file = self.csv_writer.write_data(
                    curve_data, 
                    f"distribution_curve_{xml_file.stem}"
                )
                output_files.append(curve_file)
                print(f"Created curve data file: {Path(curve_file).name} ({len(curve_data)} points)")
                
                processed_files += 1
                
            except Exception as e:
                print(f"Error processing curve data from {xml_file.name}: {e}")
                failed_files += 1
        
        # Print summary
        print(f"\nDistribution Curve Extraction Summary:")
        print(f"Total files found: {len(xml_files)}")
        print(f"Successfully processed: {processed_files}")
        print(f"Failed to process: {failed_files}")
        print(f"Curve data files created: {len(output_files)}")
        print(f"Output directory: {self.output_dir}")
        
        return {
            'total_files': len(xml_files),
            'processed_files': processed_files,
            'failed_files': failed_files,
            'output_files': output_files,
            'output_directory': str(self.output_dir)
        }
    
    def process_all_files_to_profile_json(self, filename: str = 'user_profiles') -> Dict[str, Any]:
        """将所有XML文件的数据处理成档案模式的JSON文件。
        
        档案模式特点：
        - 心态分布曲线数据整合到一个单元格中，使用[]包围
        - 数据结构更适合档案查看和管理
        - 包含完整的用户信息和心理状态数据
        
        Args:
            filename (str): 输出JSON文件名（不含扩展名）
            
        Returns:
            Dict[str, Any]: 处理结果统计信息
        """
        xml_files = list(self.report_dir.glob('*.xml'))
        
        if not xml_files:
            print(f"No XML files found in {self.report_dir}")
            return {'processed_files': 0, 'failed_files': 0, 'output_files': []}
        
        print(f"Processing {len(xml_files)} XML files to profile JSON")
        
        all_profile_data = []
        processed_files = 0
        failed_files = 0
        
        for xml_file in xml_files:
            print(f"Processing: {xml_file.name}")
            
            try:
                # Parse XML file
                root = self.parser.parse_file(str(xml_file))
                if root is None:
                    print(f"Failed to parse {xml_file.name}")
                    failed_files += 1
                    continue
                
                # Extract data
                extractor = DataExtractor(root)
                
                # 提取常规数据
                regular_data = extractor.extract_all_data()
                
                # 提取心态分布曲线数据
                curve_data = extractor.extract_distribution_curve_data()
                
                # 提取基准曲线数据
                base_curve_data = extractor.extract_base_curve_data()
                
                # 创建档案记录（使用OrderedDict确保标准顺序）
                profile_record = OrderedDict([
                    # 1. 基本身份信息
                    ('profile_id', regular_data.get('uuid', '')),
                    ('name', regular_data.get('name', '')),
                    ('gender', regular_data.get('gender', '')),
                    ('age', regular_data.get('age', '')),
                    
                    # 2. 机构信息
                    ('company', regular_data.get('company', '')),
                    ('site', regular_data.get('site', '')),
                    
                    # 3. 测试信息
                    ('test_date', regular_data.get('date', '')),
                    ('source_file', xml_file.name),
                    ('processed_time', str(Path(xml_file).stat().st_mtime)),
                    
                    # 4. 脑疲劳状态
                    ('brain_fatigue_state', regular_data.get('brain_fatigue_state', '')),
                    
                    # 5. 情绪状态
                    ('emotion', regular_data.get('emotion', '')),
                    ('energy', regular_data.get('energy', '')),
                    
                    # 6. 情绪变化信息
                    ('emotional_variation_value', regular_data.get('emotional_variation_value', '')),
                    ('emotional_variation_decision', regular_data.get('emotional_variation_decision', '')),
                    ('emotional_variation_text', regular_data.get('emotional_variation_text', '')),
                    
                    # 7. 心态分布标题信息
                    ('distribution_curve_title', regular_data.get('distribution_curve_title', '')),
                ])
                
                # 8. 心态分布详细数据（按逻辑分组）
                # 8.1 负面情绪指标
                negative_emotions = ['不安', '压力', '怀疑', '抑制', '抑郁', '攻击性', '神经质']
                for field in negative_emotions:
                    for suffix in ['_average', '_judge', '_max', '_min', '_range_max', '_range_min']:
                        key = field + suffix
                        profile_record[key] = regular_data.get(key, '')
                
                # 8.2 正面情绪指标
                positive_emotions = ['平衡', '幸福', '能量', '自信', '自我调节']
                for field in positive_emotions:
                    for suffix in ['_average', '_judge', '_max', '_min', '_range_max', '_range_min']:
                        key = field + suffix
                        profile_record[key] = regular_data.get(key, '')
                
                # 9. 心态分布曲线数据（整合到一个单元格中）
                if curve_data:
                    # 将曲线数据格式化为字符串，使用[]包围
                    curve_points_str = '[' + ','.join([
                        f"{{id:{point.get('point_id', '')},x:{point.get('x', '')},y:{point.get('y', '')}}}"
                        for point in curve_data
                    ]) + ']'
                    profile_record['distribution_curve_data'] = curve_points_str
                    
                    # 10. 曲线数据统计信息
                    profile_record['curve_non_zero_points'] = len([p for p in curve_data if float(p.get('y', 0)) > 0])
                    
                    # 找到最大Y值点
                    max_y_point = max(curve_data, key=lambda p: float(p.get('y', 0)))
                    profile_record['curve_max_y_value'] = max_y_point.get('y', '')
                    profile_record['curve_max_y_point_id'] = max_y_point.get('point_id', '')
                    profile_record['curve_max_y_point_x'] = max_y_point.get('x', '')
                else:
                    profile_record['distribution_curve_data'] = '[]'
                    profile_record['curve_non_zero_points'] = 0
                    profile_record['curve_max_y_value'] = ''
                    profile_record['curve_max_y_point_id'] = ''
                    profile_record['curve_max_y_point_x'] = ''
                
                # 11. 基准曲线数据（标准正态分布）- 仅用于图表生成，不保存到JSON
                # base_curve_data 仅在图表生成时使用，不存储到输出文件中
                
                all_profile_data.append(profile_record)
                processed_files += 1
                
            except Exception as e:
                print(f"Error processing {xml_file.name}: {e}")
                failed_files += 1
        
        # 创建档案JSON文件
        output_files = []
        if all_profile_data:
            try:
                profile_file = self.json_writer.write_data(all_profile_data, filename)
                output_files.append(profile_file)
                print(f"Created profile report: {Path(profile_file).name}")
                print(f"Total profiles: {len(all_profile_data)}")
                
                # 显示数据统计
                if all_profile_data:
                    sample_record = all_profile_data[0]
                    total_columns = len(sample_record.keys())
                    print(f"Total columns: {total_columns}")
                    print(f"Curve data stored in single column: distribution_curve_data")
                    
            except Exception as e:
                print(f"Failed to create profile report: {e}")
        
        # Print summary
        print(f"\nProfile JSON Processing Summary:")
        print(f"Total files found: {len(xml_files)}")
        print(f"Successfully processed: {processed_files}")
        print(f"Failed to process: {failed_files}")
        print(f"Output files created: {len(output_files)}")
        print(f"Output directory: {self.output_dir}")
        
        return {
            'total_files': len(xml_files),
            'processed_files': processed_files,
            'failed_files': failed_files,
            'output_files': output_files,
            'output_directory': str(self.output_dir),
            'total_records': len(all_profile_data)
        }
    
    def process_all_files_to_single_json(self, filename: str = 'complete_report_data') -> Dict[str, Any]:
        """将所有XML文件的数据（包括常规数据和心态分布曲线数据）合并到一个JSON文件中。
        
        Args:
            filename (str): 输出JSON文件名（不含扩展名）
            
        Returns:
            Dict[str, Any]: 处理结果统计信息
        """
        xml_files = list(self.report_dir.glob('*.xml'))
        
        if not xml_files:
            print(f"No XML files found in {self.report_dir}")
            return {'processed_files': 0, 'failed_files': 0, 'output_files': []}
        
        print(f"Processing {len(xml_files)} XML files to single JSON")
        
        all_combined_data = []
        processed_files = 0
        failed_files = 0
        
        for xml_file in xml_files:
            print(f"Processing: {xml_file.name}")
            
            try:
                # Parse XML file
                root = self.parser.parse_file(str(xml_file))
                if root is None:
                    print(f"Failed to parse {xml_file.name}")
                    failed_files += 1
                    continue
                
                # Extract data
                extractor = DataExtractor(root)
                
                # 提取常规数据
                regular_data = extractor.extract_all_data()
                
                # 提取心态分布曲线数据
                curve_data = extractor.extract_distribution_curve_data()
                
                # 合并数据到一行记录中
                combined_record = {
                    # 基本信息
                    'source_file': xml_file.name,
                    'processed_time': str(Path(xml_file).stat().st_mtime),
                }
                
                # 添加常规数据
                combined_record.update(regular_data)
                
                # 添加心态分布曲线数据（整合到一个单元格中）
                if curve_data:
                    # 将曲线数据格式化为字符串，使用[]包围
                    curve_points_str = '[' + ','.join([
                        f"{{id:{point.get('point_id', '')},x:{point.get('x', '')},y:{point.get('y', '')}}}"
                        for point in curve_data
                    ]) + ']'
                    combined_record['distribution_curve_data'] = curve_points_str
                    
                    # 添加曲线数据统计信息
                    combined_record['curve_non_zero_points'] = len([p for p in curve_data if float(p.get('y', 0)) > 0])
                    
                    # 找到最大Y值点
                    max_y_point = max(curve_data, key=lambda p: float(p.get('y', 0)))
                    combined_record['curve_max_y_value'] = max_y_point.get('y', '')
                    combined_record['curve_max_y_point_id'] = max_y_point.get('point_id', '')
                    combined_record['curve_max_y_point_x'] = max_y_point.get('x', '')
                else:
                    combined_record['distribution_curve_data'] = '[]'
                    combined_record['curve_non_zero_points'] = 0
                    combined_record['curve_max_y_value'] = ''
                    combined_record['curve_max_y_point_id'] = ''
                    combined_record['curve_max_y_point_x'] = ''
                
                all_combined_data.append(combined_record)
                processed_files += 1
                
            except Exception as e:
                print(f"Error processing {xml_file.name}: {e}")
                failed_files += 1
        
        # 创建单一的合并JSON文件
        output_files = []
        if all_combined_data:
            try:
                combined_file = self.json_writer.write_data(all_combined_data, filename)
                output_files.append(combined_file)
                print(f"Created complete report: {Path(combined_file).name}")
                print(f"Total records: {len(all_combined_data)}")
                
                # 显示数据统计
                if all_combined_data:
                    sample_record = all_combined_data[0]
                    curve_columns = [k for k in sample_record.keys() if k.startswith('curve_point_')]
                    print(f"Curve data columns: {len(curve_columns)}")
                    
            except Exception as e:
                print(f"Failed to create complete report: {e}")
        
        # Print summary
        print(f"\nSingle JSON Processing Summary:")
        print(f"Total files found: {len(xml_files)}")
        print(f"Successfully processed: {processed_files}")
        print(f"Failed to process: {failed_files}")
        print(f"Output files created: {len(output_files)}")
        print(f"Output directory: {self.output_dir}")
        
        return {
            'total_files': len(xml_files),
            'processed_files': processed_files,
            'failed_files': failed_files,
            'output_files': output_files,
            'output_directory': str(self.output_dir),
            'total_records': len(all_combined_data)
        }
    
    def get_summary_statistics(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from processed data.
        
        Args:
            data_list: List of extracted data dictionaries
            
        Returns:
            Dictionary containing summary statistics
        """
        if not data_list:
            return {}
        
        stats = {
            'total_records': len(data_list),
            'unique_users': len(set(d.get('uuid', '') for d in data_list if d.get('uuid'))),
            'date_range': {
                'earliest': min(d.get('date', '') for d in data_list if d.get('date')),
                'latest': max(d.get('date', '') for d in data_list if d.get('date'))
            }
        }
        
        # Brain fatigue state distribution
        fatigue_states = [d.get('brain_fatigue_state', '') for d in data_list if d.get('brain_fatigue_state')]
        if fatigue_states:
            from collections import Counter
            stats['brain_fatigue_distribution'] = dict(Counter(fatigue_states))
        
        return stats


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m report.processor <report_directory> [output_directory]")
        sys.exit(1)
    
    report_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        processor = ReportProcessor(report_dir, output_dir)
        results = processor.process_all_files()
        
        print("\nProcessing completed successfully!")
        print(f"Results: {results}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()