"""环境变量配置模块"""
import os
from pathlib import Path
from typing import Optional
from .config import AudioConfig, APIConfig, TTSConfig

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    # 查找项目根目录的.env文件
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    env_file = project_root / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 自动加载环境配置文件: {env_file}")
except ImportError:
    # python-dotenv未安装，跳过自动加载
    pass

def load_from_env() -> TTSConfig:
    """从环境变量加载配置"""
    # 获取原始API密钥
    raw_api_key = os.getenv('TTS_API_KEY', '')
    
    # 自动添加Bearer前缀
    formatted_api_key = ''
    if raw_api_key:
        if raw_api_key.startswith('Bearer '):
            formatted_api_key = raw_api_key
        elif raw_api_key.startswith('sk-'):
            formatted_api_key = f'Bearer {raw_api_key}'
        else:
            formatted_api_key = raw_api_key  # 保持原样，让验证函数处理
    # 加载API配置
    api_config = APIConfig(
        url=os.getenv('TTS_API_URL', 'https://api.siliconflow.cn/v1/audio/speech'),
        key=formatted_api_key,
        default_model=os.getenv('TTS_DEFAULT_MODEL', 'FunAudioLLM/CosyVoice2-0.5B'),
        default_voice=os.getenv('TTS_DEFAULT_VOICE', 'FunAudioLLM/CosyVoice2-0.5B:anna')
    )
    
    # 加载音频配置
    audio_config = AudioConfig(
        rate=int(os.getenv('AUDIO_SAMPLE_RATE', '44100')),
        channels=int(os.getenv('AUDIO_CHANNELS', '1')),
        chunk=int(os.getenv('AUDIO_CHUNK_SIZE', '2048'))
    )
    
    return TTSConfig(audio=audio_config, api=api_config)

def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式"""
    if not api_key:
        return False
    
    # 支持两种格式：
    # 1. 完整格式：Bearer sk-xxx
    # 2. 简化格式：sk-xxx（会自动添加Bearer前缀）
    if api_key.startswith('Bearer sk-') and len(api_key) > 27:
        return True
    elif api_key.startswith('sk-') and len(api_key) > 20:
        return True
        
    return False

def format_api_key(api_key: str) -> str:
    """格式化API密钥，自动添加Bearer前缀"""
    if not api_key:
        return ''
    
    if api_key.startswith('Bearer '):
        return api_key
    elif api_key.startswith('sk-'):
        return f'Bearer {api_key}'
    else:
        return api_key  # 保持原样

def get_secure_config() -> TTSConfig:
    """获取安全的配置（从环境变量加载并验证）"""
    config = load_from_env()
    
    if not validate_api_key(config.api.key):
        raise ValueError(
            "无效的API密钥。请设置环境变量 TTS_API_KEY 或创建 .env 文件。\n"
            "格式：sk-your-actual-api-key-here（Bearer前缀会自动添加）\n"
            "参考 .env.example 文件进行配置。"
        )
    
    return config