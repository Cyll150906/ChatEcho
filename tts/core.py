"""TTS核心模块"""
import pyaudio
from typing import Optional
from .player import AudioPlayer
from .request_handler import TTSRequestHandler

class StreamingTTS:
    """流式TTS核心类"""
    
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=44100, chunk=2048):
        """初始化流式TTS系统"""
        # 初始化音频播放器
        self.audio_player = AudioPlayer(format, channels, rate, chunk)
        
        # 初始化请求处理器
        self.request_handler = TTSRequestHandler(self.audio_player, chunk)
        
        # 音频参数（保持向后兼容）
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = chunk
    
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
        self.request_handler.set_api_config(api_url, api_key, default_model, default_voice)
    
    def close(self):
        """关闭TTS系统"""
        self.audio_player.close()