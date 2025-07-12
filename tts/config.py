"""TTS配置模块"""
import pyaudio
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioConfig:
    """音频配置类"""
    format: int = pyaudio.paInt16
    channels: int = 1  # 单声道
    rate: int = 44100
    chunk: int = 2048

@dataclass
class APIConfig:
    """API配置类"""
    url: str = "https://api.siliconflow.cn/v1/audio/speech"
    key: str = "Bearer sk-oyxoqrxbymcizdfmfuzdxtudualgftadigummmozhhpdjamu"
    default_model: str = "FunAudioLLM/CosyVoice2-0.5B"
    default_voice: str = "FunAudioLLM/CosyVoice2-0.5B:anna"

@dataclass
class TTSConfig:
    """TTS配置类"""
    audio: AudioConfig = None
    api: APIConfig = None
    
    def __post_init__(self):
        if self.audio is None:
            self.audio = AudioConfig()
        if self.api is None:
            self.api = APIConfig()

# 默认配置实例
DEFAULT_CONFIG = TTSConfig()

# 音频格式常量
class AudioFormats:
    """音频格式常量"""
    INT16 = pyaudio.paInt16
    INT24 = pyaudio.paInt24
    INT32 = pyaudio.paInt32
    FLOAT32 = pyaudio.paFloat32

# 采样率常量
class SampleRates:
    """采样率常量"""
    RATE_8K = 8000
    RATE_16K = 16000
    RATE_22K = 22050
    RATE_44K = 44100
    RATE_48K = 48000
    RATE_96K = 96000

# 声道常量
class Channels:
    """声道常量"""
    MONO = 1
    STEREO = 2