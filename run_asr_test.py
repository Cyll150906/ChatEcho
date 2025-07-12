#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASR快速测试运行脚本

简化的ASR测试脚本，专门用于测试指定音频文件的转录功能。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_test():
    """快速ASR转录测试"""
    print("🎤 ChatEcho ASR 快速测试")
    print("=" * 40)
    
    # 指定的音频文件
    audio_file = r"D:\PythonProject\AG\temp_audio\recording_20250710_182508.wav"
    
    # 检查文件
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        print("请确认文件路径是否正确")
        return
    
    print(f"📁 测试文件: {os.path.basename(audio_file)}")
    print(f"📊 文件大小: {os.path.getsize(audio_file) / 1024:.1f} KB")
    
    try:
        # 导入ASR模块
        from asr import StreamingASR
        
        # 使用上下文管理器进行转录
        print("\n🔄 开始转录...")
        with StreamingASR.from_env() as asr:
            result = asr.transcribe_file(audio_file)
            
            print("\n✅ 转录完成!")
            print("📝 结果:")
            print("-" * 30)
            print(result)
            print("-" * 30)
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        print("💡 请检查:")
        print("  1. .env 文件中的 ASR_API_KEY 配置")
        print("  2. 网络连接")
        print("  3. 音频文件格式")

if __name__ == "__main__":
    quick_test()