#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASR功能测试脚本

测试ASR模块的各项功能，包括文件转录、设备检测等。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from asr import StreamingASR
    from asr.exceptions import ASRException, ASRTranscriptionError, ASRConfigurationError
except ImportError as e:
    print(f"❌ 导入ASR模块失败: {e}")
    print("请确保已正确安装依赖包：pip install -r requirements.txt")
    sys.exit(1)


def test_asr_transcription():
    """测试ASR转录功能"""
    print("🎤 ASR转录功能测试")
    print("=" * 50)
    
    # 音频文件路径
    audio_file = r"D:\PythonProject\AG\temp_audio\recording_20250710_182508.wav"
    
    # 检查文件是否存在
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return False
    
    # 获取文件信息
    file_size = os.path.getsize(audio_file) / (1024 * 1024)  # MB
    print(f"📁 音频文件: {audio_file}")
    print(f"📊 文件大小: {file_size:.2f} MB")
    
    try:
        # 创建ASR实例（推荐使用上下文管理器）
        print("\n🔧 初始化ASR系统...")
        with StreamingASR.from_env() as asr:
            print("✅ ASR系统初始化成功")
            
            # 测试API连接
            print("\n🌐 测试API连接...")
            if asr.test_api_connection():
                print("✅ API连接正常")
            else:
                print("⚠️ API连接测试失败，但继续尝试转录")
            
            # 获取系统信息
            print("\n📋 系统信息:")
            system_info = asr.get_system_info()
            print(f"  - 音频采样率: {system_info['config']['audio']['rate']} Hz")
            print(f"  - 音频声道: {system_info['config']['audio']['channels']}")
            print(f"  - API模型: {system_info['config']['api']['model']}")
            
            # 检测音频设备
            print("\n🔊 检测音频设备...")
            try:
                devices = asr.list_audio_devices()
                print(f"✅ 检测到 {len(devices)} 个音频设备")
                for i, device in enumerate(devices[:3]):  # 只显示前3个设备
                    print(f"  {i}: {device.get('name', 'Unknown Device')}")
                if len(devices) > 3:
                    print(f"  ... 还有 {len(devices) - 3} 个设备")
            except Exception as e:
                print(f"⚠️ 音频设备检测失败: {e}")
            
            # 开始转录
            print("\n🔄 开始转录音频文件...")
            print("⏳ 请稍候，正在处理中...")
            
            result = asr.transcribe_file(audio_file)
            
            print("\n✅ 转录完成!")
            print("📝 转录结果:")
            print("-" * 40)
            print(result)
            print("-" * 40)
            
            return True
            
    except ASRConfigurationError as e:
        print(f"\n❌ 配置错误: {e}")
        print("💡 解决建议:")
        print("  1. 检查 .env 文件是否存在")
        print("  2. 确认 ASR_API_KEY 是否正确配置")
        print("  3. 验证 API 密钥格式（应以 'sk-' 开头）")
        return False
        
    except ASRTranscriptionError as e:
        print(f"\n❌ 转录错误: {e}")
        print("💡 解决建议:")
        print("  1. 检查网络连接是否正常")
        print("  2. 确认 API 密钥是否有效")
        print("  3. 验证音频文件格式是否支持")
        print("  4. 尝试使用较小的音频文件")
        return False
        
    except ASRException as e:
        print(f"\n❌ ASR系统错误: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False


def test_environment_check():
    """测试环境检查"""
    print("🔍 环境检查")
    print("=" * 50)
    
    # 检查.env文件
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ .env 文件存在")
    else:
        print("⚠️ .env 文件不存在")
        print("💡 请复制 .env.example 为 .env 并配置API密钥")
    
    # 检查环境变量
    required_vars = ['ASR_API_KEY', 'ASR_API_URL', 'ASR_DEFAULT_MODEL']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                # 隐藏API密钥的大部分内容
                masked_value = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else value[:4] + '*' * (len(value) - 4)
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: 未设置")
    
    if missing_vars:
        print(f"\n⚠️ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    return True


def main():
    """主函数"""
    print("🎯 ChatEcho ASR 功能测试")
    print("=" * 60)
    
    # 环境检查
    env_ok = test_environment_check()
    print()
    
    if not env_ok:
        print("❌ 环境检查失败，请先配置环境变量")
        return
    
    # ASR转录测试
    success = test_asr_transcription()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ASR测试完成！转录功能正常工作")
    else:
        print("💥 ASR测试失败，请检查配置和网络连接")
    
    print("\n💡 提示:")
    print("  - 确保 .env 文件中的 ASR_API_KEY 是有效的")
    print("  - 检查网络连接是否正常")
    print("  - 音频文件应为支持的格式（WAV、MP3、FLAC等）")


if __name__ == "__main__":
    main()