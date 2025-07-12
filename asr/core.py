"""ASR核心模块

整合录音和转录功能，提供完整的语音识别解决方案。
"""

import os
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from .config import AudioConfig, APIConfig, ASRConfig
from .recorder import AudioRecorder
from .transcriber import SpeechTranscriber
from .utils import save_audio_to_file, get_temp_filename, cleanup_temp_files, get_audio_info
from .exceptions import ASRException, ASRConfigurationError, ASRRecordingError, ASRTranscriptionError
from .env_config import load_from_env, validate_config


class StreamingASR:
    """流式语音识别系统
    
    整合录音和转录功能，提供完整的语音识别解决方案。
    """
    
    def __init__(self, config: Optional[ASRConfig] = None):
        """初始化ASR系统
        
        Args:
            config: ASR配置，None表示从环境变量加载
        """
        if config is None:
            config = self._load_config_from_env()
        
        self.config = config
        self.recorder = AudioRecorder(config.audio)
        self.transcriber = SpeechTranscriber(config.api)
        
        # 确保临时目录存在
        os.makedirs(self.config.temp_dir, exist_ok=True)
        
        # 状态跟踪
        self._is_recording = False
        self._current_audio_file = None
        
        if self.config.debug:
            print(f"ASR系统初始化完成")
            print(f"音频配置: {self.config.audio.rate}Hz, {self.config.audio.channels}声道")
            print(f"API模型: {self.config.api.model}")
    
    @classmethod
    def from_env(cls) -> 'StreamingASR':
        """从环境变量创建ASR实例
        
        Returns:
            ASR实例
        """
        return cls()
    
    @classmethod
    def create_with_config(cls, audio_config: AudioConfig, api_config: APIConfig, 
                          temp_dir: str = "temp", auto_delete_temp: bool = True, 
                          debug: bool = False) -> 'StreamingASR':
        """使用指定配置创建ASR实例
        
        Args:
            audio_config: 音频配置
            api_config: API配置
            temp_dir: 临时目录
            auto_delete_temp: 是否自动删除临时文件
            debug: 是否启用调试模式
            
        Returns:
            ASR实例
        """
        config = ASRConfig(
            audio=audio_config,
            api=api_config,
            temp_dir=temp_dir,
            auto_delete_temp=auto_delete_temp,
            debug=debug
        )
        return cls(config)
    
    def _load_config_from_env(self) -> ASRConfig:
        """从环境变量加载配置
        
        Returns:
            ASR配置
        """
        from .env_config import load_asr_config_from_env
        return load_asr_config_from_env()
    
    def start_recording(self) -> bool:
        """开始录音
        
        Returns:
            是否成功开始录音
        """
        if self._is_recording:
            if self.config.debug:
                print("⚠️ 已经在录音中")
            return False
        
        try:
            success = self.recorder.start_recording()
            if success:
                self._is_recording = True
                if self.config.debug:
                    print("🎤 开始录音...")
            return success
        except Exception as e:
            if self.config.debug:
                print(f"❌ 开始录音失败: {e}")
            raise
    
    def stop_recording(self) -> Optional[str]:
        """停止录音并保存文件
        
        Returns:
            录音文件路径，失败返回None
        """
        if not self._is_recording:
            if self.config.debug:
                print("⚠️ 当前没有在录音")
            return None
        
        try:
            # 停止录音获取音频数据
            audio_data = self.recorder.stop_recording()
            self._is_recording = False
            
            # 保存到临时文件
            temp_file = get_temp_filename(
                prefix="recording_",
                suffix=".wav",
                temp_dir=self.config.temp_dir
            )
            
            save_audio_to_file(
                audio_data, temp_file,
                channels=self.config.audio.channels,
                sample_width=self.config.audio.format_bits // 8,
                frame_rate=self.config.audio.rate
            )
            
            self._current_audio_file = temp_file
            
            if self.config.debug:
                print(f"🛑 停止录音")
                print(f"💾 录音已保存: {temp_file}")
            
            return temp_file
            
        except Exception as e:
            self._is_recording = False
            if self.config.debug:
                print(f"❌ 停止录音失败: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path: str, **kwargs) -> str:
        """转录音频文件
        
        Args:
            audio_file_path: 音频文件路径
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        try:
            if self.config.debug:
                info = get_audio_info(audio_file_path)
                print(f"🔄 正在转录音频文件: {audio_file_path}")
                print(f"文件大小: {info['file_size_mb']:.1f}MB")
                if 'duration' in info:
                    print(f"音频时长: {info['duration']:.1f}秒")
            
            text = self.transcriber.transcribe_file(audio_file_path, **kwargs)
            
            if self.config.debug:
                print(f"✅ 转录成功: {text}")
            
            return text
            
        except Exception as e:
            if self.config.debug:
                print(f"❌ 转录失败: {e}")
            raise
    
    def transcribe_bytes(self, audio_data: bytes, filename: str = "audio.wav", **kwargs) -> str:
        """转录音频字节数据
        
        Args:
            audio_data: 音频字节数据
            filename: 文件名（用于API识别格式）
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        try:
            if self.config.debug:
                print(f"🔄 正在转录音频数据: {len(audio_data)} 字节")
            
            text = self.transcriber.transcribe_bytes(audio_data, filename, **kwargs)
            
            if self.config.debug:
                print(f"✅ 转录成功: {text}")
            
            return text
            
        except Exception as e:
            if self.config.debug:
                print(f"❌ 转录失败: {e}")
            raise
    
    def record_and_transcribe(self, duration: Optional[float] = None, 
                             auto_delete: Optional[bool] = None, **kwargs) -> str:
        """录音并转录（一键完成）
        
        Args:
            duration: 录音时长（秒），None表示手动停止
            auto_delete: 是否自动删除录音文件，None表示使用配置默认值
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        if auto_delete is None:
            auto_delete = self.config.auto_delete_temp
        
        audio_file = None
        try:
            # 开始录音
            if not self.start_recording():
                raise ASRRecordingError("无法开始录音")
            
            if duration:
                # 自动录音指定时长
                if self.config.debug:
                    print(f"⏱️ 将录音 {duration} 秒...")
                time.sleep(duration)
            else:
                # 手动停止录音
                if self.config.debug:
                    print("按 Enter 键停止录音...")
                input()
            
            # 停止录音
            audio_file = self.stop_recording()
            if not audio_file:
                raise ASRRecordingError("录音失败")
            
            # 转录
            text = self.transcribe_audio(audio_file, **kwargs)
            
            return text
            
        except KeyboardInterrupt:
            if self.config.debug:
                print("\n⚠️ 用户中断录音")
            if self._is_recording:
                self.stop_recording()
            raise ASRException("用户中断录音")
        finally:
            # 清理临时文件
            if auto_delete and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    if self.config.debug:
                        print(f"🗑️ 已删除录音文件: {audio_file}")
                except Exception as e:
                    if self.config.debug:
                        print(f"⚠️ 删除录音文件失败: {e}")
    
    def transcribe_file(self, file_path: str, auto_delete: bool = False, **kwargs) -> str:
        """转录已有音频文件
        
        Args:
            file_path: 音频文件路径
            auto_delete: 是否自动删除音频文件
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        try:
            text = self.transcribe_audio(file_path, **kwargs)
            
            if auto_delete and text and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    if self.config.debug:
                        print(f"🗑️ 已删除音频文件: {file_path}")
                except Exception as e:
                    if self.config.debug:
                        print(f"⚠️ 删除音频文件失败: {e}")
            
            return text
            
        except Exception as e:
            if self.config.debug:
                print(f"❌ 文件转录失败: {e}")
            raise
    
    def get_device_list(self) -> list:
        """获取可用音频设备列表
        
        Returns:
            设备信息列表
        """
        return self.recorder.get_device_list()
    
    def list_audio_devices(self) -> list:
        """获取可用音频设备列表（别名方法）
        
        Returns:
            设备信息列表
        """
        return self.get_device_list()
    
    def test_device(self, device_index: Optional[int] = None) -> bool:
        """测试音频设备
        
        Args:
            device_index: 设备索引，None表示使用当前配置的设备
            
        Returns:
            设备是否可用
        """
        if device_index is None:
            device_index = self.config.audio.device_index
        return self.recorder.test_device(device_index)
    
    def test_api_connection(self) -> bool:
        """测试API连接
        
        Returns:
            连接是否正常
        """
        return self.transcriber.test_connection()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息
        
        Returns:
            系统信息字典
        """
        return {
            'config': {
                'audio': {
                    'rate': self.config.audio.rate,
                    'channels': self.config.audio.channels,
                    'chunk': self.config.audio.chunk,
                    'format_bits': self.config.audio.format_bits,
                    'device_index': self.config.audio.device_index
                },
                'api': {
                    'url': self.config.api.url,
                    'model': self.config.api.model,
                    'timeout': self.config.api.timeout,
                    'max_retries': self.config.api.max_retries
                },
                'temp_dir': self.config.temp_dir,
                'auto_delete_temp': self.config.auto_delete_temp,
                'debug': self.config.debug
            },
            'recorder': {
                'initialized': hasattr(self, 'recorder') and self.recorder is not None
            },
            'transcriber': {
                'initialized': hasattr(self, 'transcriber') and self.transcriber is not None
            },
            'status': {
                'is_recording': self._is_recording,
                'current_audio_file': self._current_audio_file,
                'api_connection': self.test_api_connection()
            },
            'devices': self.get_device_list()
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理临时文件
        
        Args:
            max_age_hours: 最大保留时间（小时）
        """
        cleanup_temp_files(self.config.temp_dir, max_age_hours=max_age_hours)
        if self.config.debug:
            print(f"🧹 已清理临时文件（保留时间: {max_age_hours}小时）")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def close(self):
        """关闭ASR系统，清理资源"""
        if self._is_recording:
            try:
                self.stop_recording()
            except Exception:
                pass
        
        # 清理当前音频文件
        if (self.config.auto_delete_temp and 
            self._current_audio_file and 
            os.path.exists(self._current_audio_file)):
            try:
                os.remove(self._current_audio_file)
                if self.config.debug:
                    print(f"🗑️ 已清理当前音频文件: {self._current_audio_file}")
            except Exception as e:
                if self.config.debug:
                    print(f"⚠️ 清理音频文件失败: {e}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()