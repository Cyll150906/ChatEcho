"""TTS请求处理模块"""
import requests
import threading
import time
from typing import Optional
from .audio_utils import parse_wav_header

class TTSRequestHandler:
    """TTS请求处理器类"""
    
    def __init__(self, audio_player, chunk_size=2048):
        """初始化请求处理器"""
        self.audio_player = audio_player
        self.chunk_size = chunk_size
        
        # API配置
        self.api_url = "https://api.siliconflow.cn/v1/audio/speech"
        self.api_key = "Bearer sk-oyxoqrxbymcizdfmfuzdxtudualgftadigummmozhhpdjamu"
        self.default_model = "FunAudioLLM/CosyVoice2-0.5B"
        self.default_voice = "FunAudioLLM/CosyVoice2-0.5B:anna"
    
    def _process_stream_response(self, response, request_id):
        """处理单个流式响应"""
        audio_buffer = bytearray()
        wav_header_parsed = False
        
        try:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_buffer.extend(chunk)
                    
                    # 如果还没有解析WAV头
                    if not wav_header_parsed and len(audio_buffer) >= 44:
                        data_start = parse_wav_header(audio_buffer)
                        if data_start is not None:
                            wav_header_parsed = True
                            # WAV头解析成功，移除WAV头，只保留音频数据
                            audio_buffer = audio_buffer[data_start:]
                    
                    # 如果有足够的音频数据且已解析头部
                    if wav_header_parsed and len(audio_buffer) >= self.chunk_size * 2:
                        # 取出音频数据块放入播放队列
                        while len(audio_buffer) >= self.chunk_size * 2:
                            chunk_size = self.chunk_size * 2
                            audio_chunk = bytes(audio_buffer[:chunk_size])
                            audio_buffer = audio_buffer[chunk_size:]
                            
                            # 将音频块加入播放队列
                            self.audio_player.add_audio_chunk(audio_chunk)
            
            # 处理剩余的音频数据
            if wav_header_parsed and len(audio_buffer) > 0:
                self.audio_player.add_audio_chunk(bytes(audio_buffer))
            
        except Exception as e:
            print(f"处理流式响应时出错: {e}")
    
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
            self.api_key = api_key
        if default_model:
            self.default_model = default_model
        if default_voice:
            self.default_voice = default_voice