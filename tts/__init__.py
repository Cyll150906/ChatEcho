# 核心类
from .core import StreamingTTS
from .player import AudioPlayer
from .request_handler import TTSRequestHandler

# 配置类
from .config import (
    AudioConfig, 
    APIConfig, 
    TTSConfig, 
    DEFAULT_CONFIG,
    AudioFormats,
    SampleRates,
    Channels
)

# 异常类
from .exceptions import (
    TTSError,
    AudioError,
    AudioInitError,
    AudioPlaybackError,
    RequestError,
    APIError,
    NetworkError,
    AuthenticationError,
    RateLimitError,
    ConfigError,
    InvalidConfigError
)

# 工具函数
from .utils import (
    generate_request_id,
    save_audio_to_file,
    load_audio_from_file,
    calculate_audio_duration,
    convert_audio_format,
    validate_audio_config,
    format_duration,
    get_file_size_mb
)

# 音频工具函数
from .audio_utils import parse_wav_header

# 导入环境配置
from .env_config import load_from_env, validate_api_key, get_secure_config, format_api_key

__version__ = "1.0.0"

__all__ = [
    # 核心类
    'StreamingTTS',
    'AudioPlayer', 
    'TTSRequestHandler',
    
    # 配置类
    'AudioConfig',
    'APIConfig', 
    'TTSConfig',
    'DEFAULT_CONFIG',
    'AudioFormats',
    'SampleRates',
    'Channels',
    
    # 异常类
    'TTSError',
    'AudioError',
    'AudioInitError', 
    'AudioPlaybackError',
    'RequestError',
    'APIError',
    'NetworkError',
    'AuthenticationError',
    'RateLimitError',
    'ConfigError',
    'InvalidConfigError',
    
    # 工具函数
    'generate_request_id',
    'save_audio_to_file',
    'load_audio_from_file', 
    'calculate_audio_duration',
    'convert_audio_format',
    'validate_audio_config',
    'format_duration',
    'get_file_size_mb',
    'parse_wav_header'
]