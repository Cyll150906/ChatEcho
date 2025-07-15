"""TTS核心模块"""
import pyaudio
from typing import Optional, Union
from .player import AudioPlayer
from .request_handler import TTSRequestHandler
from .config import TTSConfig, DEFAULT_CONFIG
from .env_config import format_api_key

class StreamingTTS:
    """流式TTS核心类"""
    
    def __init__(self, config: Optional[TTSConfig] = None, 
                 format=pyaudio.paInt16, channels=1, rate=44100, chunk=2048):
        """初始化流式TTS系统
        
        Args:
            config: TTS配置对象，如果提供则优先使用
            format: 音频格式（当config为None时使用）
            channels: 声道数（当config为None时使用）
            rate: 采样率（当config为None时使用）
            chunk: 缓冲区大小（当config为None时使用）
        """
        # 确定使用的配置
        if config is not None:
            audio_config = config.audio
            api_config = config.api
        else:
            # 使用传入的参数或默认配置
            audio_config = DEFAULT_CONFIG.audio
            audio_config.format = format
            audio_config.channels = channels
            audio_config.rate = rate
            audio_config.chunk = chunk
            api_config = DEFAULT_CONFIG.api
        
        # 初始化音频播放器
        self.audio_player = AudioPlayer(
            audio_config.format, 
            audio_config.channels, 
            audio_config.rate, 
            audio_config.chunk
        )
        
        # 初始化请求处理器
        self.request_handler = TTSRequestHandler(self.audio_player, audio_config.chunk)
        
        # 如果提供了配置，设置API配置
        if config is not None and api_config.key:
            self.request_handler.set_api_config(
                api_config.url,
                api_config.key,
                api_config.default_model,
                api_config.default_voice
            )
        else:
            # 尝试从环境变量加载配置
            try:
                from .env_config import load_from_env
                env_config = load_from_env()
                if env_config.api.key:
                    self.request_handler.set_api_config(
                        env_config.api.url,
                        env_config.api.key,
                        env_config.api.default_model,
                        env_config.api.default_voice
                    )
            except Exception as e:
                print(f"警告：无法加载环境配置: {e}")
        
        # 音频参数（保持向后兼容）
        self.FORMAT = audio_config.format
        self.CHANNELS = audio_config.channels
        self.RATE = audio_config.rate
        self.CHUNK = audio_config.chunk
    
    def send_tts_request(self, text: str, request_id: Optional[str] = None,
                        model: Optional[str] = None, voice: Optional[str] = None,
                        speed: float = 1.0, gain: float = 0.0, sample_rate: int = 44100):
        """发送TTS请求并开始流式播放"""
        return self.request_handler.send_tts_request(
            text, request_id, model, voice, speed, gain, sample_rate
        )
    
    def stop_current_playback(self):
        """停止当前播放并清空音频队列"""
        self.audio_player.stop_current_playback()
    
    def pause(self):
        """暂停播放"""
        self.audio_player.pause()
    
    def resume(self):
        """恢复播放"""
        self.audio_player.resume()
    
    def is_playing(self):
        """检查是否正在播放音频"""
        return self.audio_player.is_playing()
    
    def wait_for_completion(self):
        """等待所有音频播放完成"""
        self.audio_player.wait_for_completion()
    
    def set_api_config(self, api_url: Optional[str] = None, api_key: Optional[str] = None,
                      default_model: Optional[str] = None, default_voice: Optional[str] = None):
        """设置API配置"""
        # 格式化API密钥
        if api_key is not None:
            api_key = format_api_key(api_key)
        self.request_handler.set_api_config(api_url, api_key, default_model, default_voice)
    
    def synthesize(self, text: str, output_path: str, model: Optional[str] = None, 
                   voice: Optional[str] = None, speed: float = 1.0, gain: float = 0.0, 
                   sample_rate: int = 44100):
        """合成语音并保存到文件
        
        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            model: 模型名称
            voice: 音色
            speed: 语速
            gain: 音量增益
            sample_rate: 采样率
        """
        import requests
        import tempfile
        from .utils import save_audio_to_file
        
        # 构建请求参数
        payload = {
            "input": text,
            "response_format": "wav",
            "sample_rate": sample_rate,
            "stream": False,  # 非流式，获取完整音频
            "speed": speed,
            "gain": gain,
            "model": model or self.request_handler.default_model,
            "voice": voice or self.request_handler.default_voice
        }
        
        headers = {
            "Authorization": self.request_handler.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            # 发送请求获取音频数据
            response = requests.post(self.request_handler.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # 保存音频数据到文件
            with open(output_path, 'wb') as f:
                f.write(response.content)
                
        except Exception as e:
            raise Exception(f"TTS合成失败: {str(e)}")
    
    def close(self):
        """关闭TTS系统"""
        self.audio_player.close()