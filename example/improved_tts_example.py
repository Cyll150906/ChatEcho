"""改进的TTS使用示例 - 展示最佳实践"""
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 已加载环境配置: {env_file}")
except ImportError:
    print("💡 建议安装python-dotenv以支持.env文件")

from tts import (
    StreamingTTS,
    TTSConfig,
    AudioConfig,
    APIConfig,
    get_secure_config,
    validate_api_key,
    TTSError,
    AuthenticationError,
    AudioError
)

def method1_environment_config():
    """方法1: 使用环境变量配置（推荐）"""
    print("\n=== 方法1: 环境变量配置 ===")
    
    try:
        # 从环境变量加载安全配置
        config = get_secure_config()
        print("✅ 环境配置加载成功")
        
        # 使用配置创建TTS实例
        tts = StreamingTTS(config=config)
        
        # 发送请求
        text = "使用环境变量配置的TTS系统测试。"
        request_id = tts.send_tts_request(text)
        
        if request_id:
            print(f"✅ 请求成功: {request_id}")
            tts.wait_for_completion()
            print("✅ 播放完成")
        
        tts.close()
        return True
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except AuthenticationError as e:
        print(f"🔐 认证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def method2_manual_config():
    """方法2: 手动创建配置对象"""
    print("\n=== 方法2: 手动配置对象 ===")
    
    # 检查API密钥
    api_key = os.getenv('TTS_API_KEY', '')
    if not validate_api_key(api_key):
        print("❌ 需要有效的API密钥")
        return False
    
    try:
        # 创建自定义音频配置
        audio_config = AudioConfig(
            rate=48000,  # 更高的采样率
            channels=1,
            chunk=4096   # 更大的缓冲区
        )
        
        # 创建API配置（只需要传入sk-开头的密钥，Bearer前缀会自动添加）
        api_config = APIConfig(
            url=os.getenv('TTS_API_URL', 'https://api.siliconflow.cn/v1/audio/speech'),
            key=api_key,
            default_model=os.getenv('TTS_DEFAULT_MODEL', 'FunAudioLLM/CosyVoice2-0.5B'),
            default_voice=os.getenv('TTS_DEFAULT_VOICE', 'FunAudioLLM/CosyVoice2-0.5B:anna')
        )
        
        # 创建完整配置
        config = TTSConfig(audio=audio_config, api=api_config)
        print(f"✅ 自定义配置创建成功 (采样率: {config.audio.rate}Hz)")
        
        # 使用配置创建TTS实例
        tts = StreamingTTS(config=config)
        
        # 发送请求
        text = "使用自定义配置的高质量TTS测试。"
        request_id = tts.send_tts_request(text, speed=1.1, gain=0.1)
        
        if request_id:
            print(f"✅ 请求成功: {request_id}")
            tts.wait_for_completion()
            print("✅ 播放完成")
        
        tts.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def method3_legacy_compatibility():
    """方法3: 传统方式（向后兼容）"""
    print("\n=== 方法3: 传统方式（向后兼容） ===")
    
    api_key = os.getenv('TTS_API_KEY', '')
    if not validate_api_key(api_key):
        print("❌ 需要有效的API密钥")
        return False
    
    try:
        # 使用传统方式创建（不传入config）
        tts = StreamingTTS(rate=44100, chunk=2048)
        
        # 手动设置API配置（只需要传入sk-开头的密钥，Bearer前缀会自动添加）
        tts.set_api_config(
            api_key=api_key,
            api_url=os.getenv('TTS_API_URL', 'https://api.siliconflow.cn/v1/audio/speech')
        )
        
        print("✅ 传统方式初始化成功")
        
        # 发送请求
        text = "传统方式的TTS系统测试。"
        request_id = tts.send_tts_request(text)
        
        if request_id:
            print(f"✅ 请求成功: {request_id}")
            tts.wait_for_completion()
            print("✅ 播放完成")
        
        tts.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def advanced_features_demo():
    """高级功能演示"""
    print("\n=== 高级功能演示 ===")
    
    try:
        config = get_secure_config()
        tts = StreamingTTS(config=config)
        
        # 1. 播放控制演示
        print("🎵 播放控制演示...")
        long_text = "这是一段较长的文本，用于演示播放控制功能。" * 3
        request_id = tts.send_tts_request(long_text)
        
        if request_id:
            time.sleep(1)
            print("⏸️ 暂停播放")
            tts.pause()
            
            time.sleep(2)
            print("▶️ 恢复播放")
            tts.resume()
            
            time.sleep(1)
            print("⏹️ 停止播放")
            tts.stop_current_playback()
        
        # 2. 多语音测试
        print("\n🗣️ 多语音测试...")
        voices = [
            "FunAudioLLM/CosyVoice2-0.5B:anna",
            "FunAudioLLM/CosyVoice2-0.5B:bella"
        ]
        
        for i, voice in enumerate(voices, 1):
            text = f"这是第{i}个语音测试。"
            request_id = tts.send_tts_request(text, voice=voice)
            if request_id:
                print(f"✅ 语音{i}请求成功: {request_id}")
                tts.wait_for_completion()  # 等待当前语音播放完成
                print(f"✅ 语音{i}播放完成")
                time.sleep(0.5)  # 短暂间隔
        tts.close()
        
    except Exception as e:
        print(f"❌ 高级功能演示失败: {e}")

def error_handling_demo():
    """错误处理演示"""
    print("\n=== 错误处理演示 ===")
    
    # 1. 无效API密钥测试
    print("🔑 测试无效API密钥...")
    try:
        invalid_config = TTSConfig(
            api=APIConfig(key="invalid_key")  # 无效密钥（不是sk-开头）
        )
        tts = StreamingTTS(config=invalid_config)
        result = tts.send_tts_request("测试文本")
        if result is None:
            print("✅ 正确处理了无效API密钥")
        tts.close()
    except Exception as e:
        print(f"✅ 捕获到预期错误: {type(e).__name__}")
    
    # 2. 空文本测试
    print("\n📝 测试空文本...")
    try:
        config = get_secure_config()
        tts = StreamingTTS(config=config)
        result = tts.send_tts_request("")
        if result is None:
            print("✅ 正确处理了空文本")
        tts.close()
    except Exception as e:
        print(f"✅ 捕获到预期错误: {type(e).__name__}")

def performance_tips():
    """性能优化提示"""
    print("\n=== 性能优化提示 ===")
    print("💡 性能优化建议:")
    print("   1. 使用更大的chunk_size (4096-8192) 减少I/O开销")
    print("   2. 对于批量请求，复用同一个TTS实例")
    print("   3. 考虑实现音频缓存机制")
    print("   4. 监控API调用频率，避免触发限流")
    print("   5. 在生产环境中使用连接池")

def main():
    """主函数"""
    print("🚀 改进的TTS使用示例")
    print("=" * 60)
    
    # 检查环境
    api_key = os.getenv('TTS_API_KEY', '')
    if not api_key:
        print("⚠️  未设置TTS_API_KEY环境变量")
        print("请参考.env.example文件配置环境变量")
        return
    
    if not validate_api_key(api_key):
        print("❌ API密钥格式无效")
        return
    
    print("✅ 环境检查通过")
    
    # 运行示例
    methods = [
        ("环境变量配置", method1_environment_config),
        ("手动配置对象", method2_manual_config),
        ("传统方式", method3_legacy_compatibility)
    ]
    
    success_count = 0
    for name, method in methods:
        try:
            print(f"\n🧪 测试 {name}...")
            if method():
                success_count += 1
                print(f"✅ {name} 测试成功")
            else:
                print(f"❌ {name} 测试失败")
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
            break
        except Exception as e:
            print(f"❌ {name} 测试异常: {e}")
    
    # 运行高级功能和错误处理演示
    if success_count > 0:
        try:
            advanced_features_demo()
            error_handling_demo()
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
    
    # 显示性能提示
    performance_tips()
    
    print(f"\n📊 测试结果: {success_count}/{len(methods)} 个方法成功")
    print("✅ 示例运行完成")

if __name__ == "__main__":
    main()