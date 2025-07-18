#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
档案模式CSV生成示例

此脚本演示如何使用ReportProcessor类的process_all_files_to_profile_csv方法
将XML报告数据处理成档案模式的CSV文件。

档案模式特点：
- 心态分布曲线数据整合到一个单元格中，使用[]包围
- 列顺序标准化，按逻辑分组排列
- 数据结构更适合档案查看和管理
"""

import os
from pathlib import Path
from report.processor import ReportProcessor

def main():
    """主函数：生成档案模式CSV文件"""
    
    # 设置路径
    current_dir = Path(__file__).parent
    xml_dir = current_dir / "reportFile"  # XML文件目录
    output_dir = current_dir / "profile_csv_output"  # 输出目录
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    print("=== 档案模式CSV生成示例 ===")
    print(f"XML文件目录: {xml_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 检查XML目录是否存在
    if not xml_dir.exists():
        print(f"错误：XML文件目录不存在: {xml_dir}")
        return
    
    try:
        # 创建处理器实例
        processor = ReportProcessor(
            report_dir=str(xml_dir),
            output_dir=str(output_dir)
        )
        
        # 处理所有XML文件并生成档案模式CSV
        print("开始处理XML文件...")
        result = processor.process_all_files_to_profile_csv('user_profiles')
        
        # 显示处理结果
        print("\n=== 处理结果 ===")
        print(f"总文件数: {result.get('total_files', 0)}")
        print(f"成功处理: {result.get('processed_files', 0)}")
        print(f"处理失败: {result.get('failed_files', 0)}")
        print(f"输出文件: {len(result.get('output_files', []))}")
        
        if result.get('output_files'):
            for output_file in result['output_files']:
                file_path = Path(output_file)
                print(f"  - {file_path.name}")
                print(f"    完整路径: {file_path}")
        
        print(f"\n输出目录: {output_dir}")
        print("\n档案模式CSV文件生成完成！")
        print("\n特点：")
        print("- 列顺序已标准化，按逻辑分组")
        print("- 心态分布曲线数据整合到单个单元格")
        print("- 负面情绪指标和正面情绪指标分组排列")
        print("- 适合档案管理和数据分析")
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()