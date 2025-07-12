"""ASR配置模块

定义ASR系统的配置数据类，包括音频配置、API配置等。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioConfig:
    """音频配置"""
    rate: int = 44100          # 采样率
    channels: int = 1          # 声道数
    chunk: int = 1024          # 音频块大小
    format_bits: int = 16      # 位深度
    device_index: Optional[int] = None  # 音频设备索引
    
    def __post_init__(self):
        """验证配置参数"""
        if self.rate <= 0:
            raise ValueError("采样率必须大于0")
        if self.channels not in [1, 2]:
            raise ValueError("声道数必须是1或2")
        if self.chunk <= 0:
            raise ValueError("音频块大小必须大于0")
        if self.format_bits not in [8, 16, 24, 32]:
            raise ValueError("位深度必须是8、16、24或32")


@dataclass
class APIConfig:
    """API配置"""
    url: str = "https://api.siliconflow.cn/v1/audio/transcriptions"
    key: str = ""
    model: str = "FunAudioLLM/SenseVoiceSmall"
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        """验证配置参数"""
        if not self.url:
            raise ValueError("API URL不能为空")
        if not self.key:
            raise ValueError("API密钥不能为空")
        if self.timeout <= 0:
            raise ValueError("超时时间必须大于0")
        if self.max_retries < 0:
            raise ValueError("重试次数不能小于0")


@dataclass
class ASRConfig:
    """ASR系统配置"""
    audio: AudioConfig
    api: APIConfig
    temp_dir: str = "temp"
    auto_delete_temp: bool = True
    debug: bool = False
    
    def __post_init__(self):
        """验证配置参数"""
        if not isinstance(self.audio, AudioConfig):
            raise TypeError("audio必须是AudioConfig实例")
        if not isinstance(self.api, APIConfig):
            raise TypeError("api必须是APIConfig实例")
        if not self.temp_dir:
            raise ValueError("临时目录路径不能为空")