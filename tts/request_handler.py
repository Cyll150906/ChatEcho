"""TTS请求处理模块"""
import requests
import threading
import time
from typing import Optional
from .audio_utils import parse_wav_header
from .config import DEFAULT_CONFIG
from .env_config import format_api_key

class TTSRequestHandler:
    """TTS请求处理器类"""
    
    def __init__(self, audio_player, chunk_size=2048):
        """初始化请求处理器"""
        self.audio_player = audio_player
        self.chunk_size = chunk_size
        
        # API配置 - 使用默认配置，避免硬编码
        self.api_url = DEFAULT_CONFIG.api.url
        self.api_key = DEFAULT_CONFIG.api.key
        self.default_model = DEFAULT_CONFIG.api.default_model
        self.default_voice = DEFAULT_CONFIG.api.default_voice
    
    def _process_stream_response(self, response, request_id):
        """处理单个流式响应"""
        audio_buffer = bytearray()
        wav_header_parsed = False
        data_start_pos = 0
        
        try:
            print(f"🎵 开始处理音频流: {request_id}")
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_buffer.extend(chunk)
                    
                    # 如果还没有解析WAV头
                    if not wav_header_parsed and len(audio_buffer) >= 44:
                        data_start_pos = parse_wav_header(audio_buffer)
                        if data_start_pos is not None:
                            wav_header_parsed = True
                            print(f"✅ WAV头解析成功，数据开始位置: {data_start_pos}")
                    
                    # 如果已解析WAV头，处理音频数据
                    if wav_header_parsed:
                        # 获取纯音频数据（跳过WAV头）
                        audio_data = audio_buffer[data_start_pos:]
                        
                        # 如果有足够的音频数据
                        if len(audio_data) >= self.chunk_size:
                            # 取出音频数据块放入播放队列
                            while len(audio_data) >= self.chunk_size:
                                audio_chunk = bytes(audio_data[:self.chunk_size])
                                audio_data = audio_data[self.chunk_size:]
                                
                                # 将音频块加入播放队列
                                self.audio_player.add_audio_chunk(audio_chunk)
                            
                            # 更新缓冲区，保留WAV头和剩余数据
                            audio_buffer = audio_buffer[:data_start_pos] + audio_data
            
            # 处理剩余的音频数据
            if wav_header_parsed:
                remaining_data = audio_buffer[data_start_pos:]
                if len(remaining_data) > 0:
                    self.audio_player.add_audio_chunk(bytes(remaining_data))
                    print(f"✅ 处理完成，剩余数据: {len(remaining_data)} 字节")
            
            print(f"🎵 音频流处理完成: {request_id}")
            
        except Exception as e:
            print(f"❌ 处理流式响应时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def send_tts_request(self, text: str, request_id: Optional[str] = None, 
                        model: Optional[str] = None, voice: Optional[str] = None,
                        speed: float = 1.0, gain: float = 0.0, sample_rate: int = 44100):
        """发送TTS请求并开始流式播放"""
        if request_id is None:
            request_id = f"req_{int(time.time() * 1000)}"
        
        payload = {
            "input": text,
            "response_format": "wav",
            "sample_rate": sample_rate,
            "stream": True,
            "speed": speed,
            "gain": gain,
            "model": model or self.default_model,
            "voice": voice or self.default_voice
        }
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            # 发送请求
            response = requests.post(self.api_url, json=payload, headers=headers, stream=True)
            response.raise_for_status()
            
            # 在新线程中处理流式响应
            thread = threading.Thread(
                target=self._process_stream_response,
                args=(response, request_id),
                daemon=True
            )
            thread.start()
            
            return request_id
            
        except Exception as e:
            print(f"发送TTS请求时出错: {e}")
            return None
    
    def set_api_config(self, api_url: Optional[str] = None, api_key: Optional[str] = None,
                      default_model: Optional[str] = None, default_voice: Optional[str] = None):
        """设置API配置"""
        if api_url:
            self.api_url = api_url
        if api_key:
            self.api_key = format_api_key(api_key)  # 自动格式化API密钥
        if default_model:
            self.default_model = default_model
        if default_voice:
            self.default_voice = default_voice