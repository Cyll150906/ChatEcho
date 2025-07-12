"""安全的TTS使用示例 - 使用环境变量配置"""
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 尝试加载.env文件（如果存在）
try:
    from dotenv import load_dotenv
    env_file = project_root / '.env'
    print(env_file)
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 已加载环境配置文件: {env_file}")
    else:
        print(f"⚠️  未找到.env文件: {env_file}")
        print("请复制.env.example为.env并配置您的API密钥")
except ImportError:
    print("💡 建议安装python-dotenv: pip install python-dotenv")

from tts import (
    StreamingTTS,
    get_secure_config,
    validate_api_key,
    TTSError,
    AuthenticationError
)

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    api_key = os.getenv('TTS_API_KEY', '')
    if not api_key:
        print("❌ 未设置TTS_API_KEY环境变量")
        return False
    
    if not validate_api_key(api_key):
        print("❌ API密钥格式无效或为示例密钥")
        print("请设置有效的API密钥到TTS_API_KEY环境变量")
        return False
    
    print("✅ API密钥验证通过")
    return True

def secure_basic_example():
    """安全的基础使用示例"""
    print("\n=== 安全的基础使用示例 ===")
    
    try:
        # 使用安全配置
        config = get_secure_config()
        print(f"✅ 配置加载成功")
        print(f"📡 API URL: {config.api.url}")
        print(f"🎵 默认模型: {config.api.default_model}")
        print(f"🔊 音频配置: {config.audio.rate}Hz, {config.audio.channels}声道")
        
        # 创建TTS实例
        tts = StreamingTTS(
            format=config.audio.format,
            channels=config.audio.channels,
            rate=config.audio.rate,
            chunk=config.audio.chunk
        )
        
        # 设置API配置
        tts.set_api_config(
            api_url=config.api.url,
            api_key=config.api.key,
            default_model=config.api.default_model,
            default_voice=config.api.default_voice
        )
        
        # 发送TTS请求
        text = "这是一个使用环境变量配置的安全TTS示例。"
        print(f"📝 发送文本: {text}")
        
        request_id = tts.send_tts_request(text)
        if request_id:
            print(f"✅ 请求成功: {request_id}")
            print("🎵 正在播放音频...")
            tts.wait_for_completion()
            print("✅ 播放完成")
        else:
            print("❌ 请求失败")
        
        tts.close()
        
    except AuthenticationError as e:
        print(f"🔐 认证错误: {e}")
        print("请检查您的API密钥是否正确")
    except TTSError as e:
        print(f"🎵 TTS错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def environment_info_example():
    """显示环境信息"""
    print("\n=== 环境信息 ===")
    
    env_vars = [
        'TTS_API_URL',
        'TTS_API_KEY',
        'TTS_DEFAULT_MODEL',
        'TTS_DEFAULT_VOICE',
        'AUDIO_SAMPLE_RATE',
        'AUDIO_CHANNELS',
        'AUDIO_CHUNK_SIZE'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var == 'TTS_API_KEY' and value:
            # 隐藏API密钥的敏感部分
            masked_value = value[:10] + '*' * (len(value) - 20) + value[-10:] if len(value) > 20 else '*' * len(value)
            print(f"🔑 {var}: {masked_value}")
        elif value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")

def setup_guide():
    """设置指南"""
    print("\n=== 设置指南 ===")
    print("1. 复制.env.example文件为.env:")
    print("   cp .env.example .env")
    print("\n2. 编辑.env文件，设置您的API密钥:")
    print("   TTS_API_KEY=sk-your-actual-api-key-here  # 只需要sk-开头的密钥，Bearer前缀会自动添加")
    print("\n3. 安装python-dotenv (可选):")
    print("   pip install python-dotenv")
    print("\n4. 运行此示例:")
    print("   python example/secure_tts_example.py")

def main():
    """主函数"""
    print("🔒 安全TTS配置示例")
    print("=" * 50)
    
    # 显示环境信息
    environment_info_example()
    
    # 检查环境配置
    if not check_environment():
        print("\n❌ 环境配置检查失败")
        setup_guide()
        return
    
    # 运行安全示例
    try:
        secure_basic_example()
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
    
    print("\n✅ 示例运行完成")

if __name__ == "__main__":
    main()