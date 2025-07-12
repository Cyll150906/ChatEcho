"""ASR (Automatic Speech Recognition) 模块

提供语音识别功能，包括录音、转录等核心功能。
设计参考TTS模块架构，实现模块化、可扩展的语音识别系统。
"""

from .config import AudioConfig, APIConfig, ASRConfig
from .core import StreamingASR
from .env_config import get_secure_config, load_from_env, validate_api_key, format_api_key
from .exceptions import ASRException, ASRConfigurationError, ASRRecordingError, ASRTranscriptionError
from .recorder import AudioRecorder
from .transcriber import SpeechTranscriber
from .utils import save_audio_to_file, load_audio_from_file, get_temp_filename

__version__ = "1.0.0"
__author__ = "ChatEcho Team"

__all__ = [
    # 配置类
    'AudioConfig',
    'APIConfig', 
    'ASRConfig',
    
    # 核心类
    'StreamingASR',
    'AudioRecorder',
    'SpeechTranscriber',
    
    # 配置函数
    'get_secure_config',
    'load_from_env',
    'validate_api_key',
    'format_api_key',
    
    # 异常类
    'ASRException',
    'ASRConfigurationError',
    'ASRRecordingError', 
    'ASRTranscriptionError',
    
    # 工具函数
    'save_audio_to_file',
    'load_audio_from_file',
    'get_temp_filename',
]