"""ASR环境配置模块

处理环境变量加载和配置验证，确保ASR系统能够正确获取配置信息。
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from .config import ASRConfig, AudioConfig, APIConfig
from .exceptions import ASRConfigurationError

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    
    # 查找项目根目录的.env文件
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # 回到ChatEcho目录
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # python-dotenv未安装时的优雅降级
    pass


def load_from_env() -> Dict[str, Any]:
    """从环境变量加载ASR配置
    
    Returns:
        包含ASR配置的字典
    """
    config = {
        # API配置
        'api_url': os.getenv('ASR_API_URL', 'https://api.siliconflow.cn/v1/audio/transcriptions'),
        'api_key': os.getenv('ASR_API_KEY', ''),
        'api_model': os.getenv('ASR_API_MODEL', 'FunAudioLLM/SenseVoiceSmall'),
        'api_timeout': int(os.getenv('ASR_API_TIMEOUT', '30')),
        'api_max_retries': int(os.getenv('ASR_API_MAX_RETRIES', '3')),
        
        # 音频配置
        'audio_rate': int(os.getenv('ASR_AUDIO_RATE', '44100')),
        'audio_channels': int(os.getenv('ASR_AUDIO_CHANNELS', '1')),
        'audio_chunk': int(os.getenv('ASR_AUDIO_CHUNK', '1024')),
        'audio_format_bits': int(os.getenv('ASR_AUDIO_FORMAT_BITS', '16')),
        'audio_device_index': os.getenv('ASR_AUDIO_DEVICE_INDEX'),
        
        # 系统配置
        'temp_dir': os.getenv('ASR_TEMP_DIR', 'temp'),
        'auto_delete_temp': os.getenv('ASR_AUTO_DELETE_TEMP', 'true').lower() == 'true',
        'debug': os.getenv('ASR_DEBUG', 'false').lower() == 'true',
    }
    
    # 处理可选的设备索引
    if config['audio_device_index']:
        try:
            config['audio_device_index'] = int(config['audio_device_index'])
        except ValueError:
            config['audio_device_index'] = None
    else:
        config['audio_device_index'] = None
    
    # 格式化API密钥
    if config['api_key'] and not config['api_key'].startswith('Bearer '):
        config['api_key'] = f"Bearer {config['api_key']}"
    
    return config


def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式
    
    Args:
        api_key: API密钥
        
    Returns:
        是否有效
    """
    if not api_key:
        return False
    
    # 移除Bearer前缀进行验证
    key = api_key.replace('Bearer ', '') if api_key.startswith('Bearer ') else api_key
    
    # 基本格式验证
    return len(key) > 10 and key.replace('-', '').replace('_', '').isalnum()


def format_api_key(api_key: str) -> str:
    """格式化API密钥，确保有Bearer前缀
    
    Args:
        api_key: 原始API密钥
        
    Returns:
        格式化后的API密钥
    """
    if not api_key:
        return api_key
    
    if api_key.startswith('Bearer '):
        return api_key
    
    return f"Bearer {api_key}"


def get_secure_config() -> Dict[str, Any]:
    """获取安全的配置信息（隐藏敏感信息）
    
    Returns:
        安全的配置字典
    """
    config = load_from_env()
    
    # 创建安全副本
    secure_config = config.copy()
    
    # 隐藏敏感信息
    if secure_config['api_key']:
        key = secure_config['api_key'].replace('Bearer ', '')
        if len(key) > 8:
            secure_config['api_key'] = f"Bearer {key[:4]}...{key[-4:]}"
        else:
            secure_config['api_key'] = "Bearer ****"
    
    return secure_config


def load_api_config_from_env() -> APIConfig:
    """从环境变量加载API配置"""
    return APIConfig(
        url=os.getenv('ASR_API_URL', 'https://api.siliconflow.cn/v1/audio/transcriptions'),
        key=os.getenv('ASR_API_KEY', ''),
        model=os.getenv('ASR_DEFAULT_MODEL', 'FunAudioLLM/SenseVoiceSmall'),
        timeout=int(os.getenv('ASR_TIMEOUT', '30')),
        max_retries=int(os.getenv('ASR_MAX_RETRIES', '3'))
    )


def load_audio_config_from_env() -> AudioConfig:
    """从环境变量加载音频配置"""
    return AudioConfig(
        rate=int(os.getenv('RECORDING_SAMPLE_RATE', '16000')),
        channels=int(os.getenv('RECORDING_CHANNELS', '1')),
        chunk=int(os.getenv('RECORDING_CHUNK_SIZE', '1024')),
        format_bits=int(os.getenv('RECORDING_FORMAT_BITS', '16'))
    )


def load_asr_config_from_env() -> ASRConfig:
    """从环境变量加载ASR配置
    
    Returns:
        ASRConfig: 完整的ASR配置对象
        
    Raises:
        ASRConfigurationError: 配置加载失败时抛出
    """
    try:
        # 加载环境变量（已在模块导入时自动加载）
        
        # 创建API配置
        api_config = load_api_config_from_env()
        
        # 创建音频配置
        audio_config = load_audio_config_from_env()
        
        # 创建完整配置
        config = ASRConfig(
            audio=audio_config,
            api=api_config
        )
        
        # 验证配置
        config_dict = {
            'api': {
                'url': config.api.url,
                'key': config.api.key,
                'model': config.api.model
            },
            'audio': {
                'rate': config.audio.rate,
                'channels': config.audio.channels
            }
        }
        is_valid, errors = validate_config(config_dict)
        if not is_valid:
             raise ASRConfigurationError(
                 f"配置验证失败: {'; '.join(errors)}"
             )
        
        return config
        
    except Exception as e:
        if isinstance(e, ASRConfigurationError):
            raise
        raise ASRConfigurationError(
             f"从环境变量加载配置失败: {e}"
         )


def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """验证配置完整性
    
    Args:
        config: 配置字典
        
    Returns:
        (是否有效, 错误信息列表)
    """
    errors = []
    
    # 验证API配置
    api_config = config.get('api', {})
    if not api_config.get('url'):
        errors.append("缺少必需的配置项: api.url")
    if not api_config.get('key'):
        errors.append("缺少必需的配置项: api.key")
    if not api_config.get('model'):
        errors.append("缺少必需的配置项: api.model")
    
    # 验证音频配置
    audio_config = config.get('audio', {})
    if audio_config.get('rate') and not (8000 <= audio_config['rate'] <= 192000):
        errors.append("audio.rate 必须在 8000 到 192000 之间")
    if audio_config.get('channels') and not (1 <= audio_config['channels'] <= 2):
        errors.append("audio.channels 必须在 1 到 2 之间")
    
    return len(errors) == 0, errors