"""ASR录音模块

封装pyaudio录音功能，提供音频设备管理、录音控制、音频格式处理等功能。
"""

import pyaudio
import wave
import threading
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from .config import AudioConfig
from .exceptions import ASRRecordingError, ASRDeviceError, ASRAudioError


class AudioRecorder:
    """音频录音器
    
    提供录音功能，支持设备管理、实时录音、音频保存等功能。
    """
    
    def __init__(self, config: AudioConfig):
        """初始化录音器
        
        Args:
            config: 音频配置
        """
        self.config = config
        self.audio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.record_thread = None
        
        # 根据位深度设置pyaudio格式
        self.format_map = {
            8: pyaudio.paInt8,
            16: pyaudio.paInt16,
            24: pyaudio.paInt24,
            32: pyaudio.paInt32
        }
        
        if config.format_bits not in self.format_map:
            raise ASRRecordingError(f"不支持的位深度: {config.format_bits}")
        
        self.format = self.format_map[config.format_bits]
    
    def _init_audio(self):
        """初始化音频设备"""
        if self.audio is None:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                raise ASRDeviceError(f"初始化音频设备失败: {e}")
    
    def _cleanup_audio(self):
        """清理音频资源"""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        
        if self.audio:
            try:
                self.audio.terminate()
            except Exception:
                pass
            self.audio = None
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        """获取可用音频设备列表
        
        Returns:
            设备信息列表
        """
        self._init_audio()
        
        devices = []
        try:
            device_count = self.audio.get_device_count()
            
            for i in range(device_count):
                try:
                    device_info = self.audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:  # 只返回输入设备
                        devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': device_info['defaultSampleRate'],
                            'is_default': i == self.audio.get_default_input_device_info()['index']
                        })
                except Exception:
                    continue
        except Exception as e:
            raise ASRDeviceError(f"获取设备列表失败: {e}")
        
        return devices
    
    def test_device(self, device_index: Optional[int] = None) -> bool:
        """测试音频设备是否可用
        
        Args:
            device_index: 设备索引，None表示使用默认设备
            
        Returns:
            设备是否可用
        """
        self._init_audio()
        
        try:
            # 尝试打开音频流
            test_stream = self.audio.open(
                format=self.format,
                channels=self.config.channels,
                rate=self.config.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.config.chunk
            )
            
            # 尝试读取一小段音频
            test_stream.read(self.config.chunk)
            test_stream.close()
            
            return True
        except Exception:
            return False
    
    def start_recording(self) -> bool:
        """开始录音
        
        Returns:
            是否成功开始录音
        """
        if self.is_recording:
            raise ASRRecordingError("已经在录音中")
        
        try:
            self._init_audio()
            
            # 测试设备是否可用
            if not self.test_device(self.config.device_index):
                available_devices = [d['name'] for d in self.get_device_list()]
                raise ASRDeviceError(
                    f"音频设备不可用: {self.config.device_index}",
                    device_index=self.config.device_index,
                    available_devices=available_devices
                )
            
            # 打开音频流
            self.stream = self.audio.open(
                format=self.format,
                channels=self.config.channels,
                rate=self.config.rate,
                input=True,
                input_device_index=self.config.device_index,
                frames_per_buffer=self.config.chunk
            )
            
            self.frames = []
            self.is_recording = True
            
            # 启动录音线程
            def record_audio():
                while self.is_recording:
                    try:
                        data = self.stream.read(self.config.chunk, exception_on_overflow=False)
                        self.frames.append(data)
                    except Exception as e:
                        if self.is_recording:  # 只在仍在录音时报告错误
                            raise ASRRecordingError(f"录音过程中出错: {e}")
                        break
            
            self.record_thread = threading.Thread(target=record_audio)
            self.record_thread.daemon = True
            self.record_thread.start()
            
            return True
            
        except Exception as e:
            self.is_recording = False
            self._cleanup_audio()
            if isinstance(e, (ASRRecordingError, ASRDeviceError)):
                raise
            else:
                raise ASRRecordingError(f"开始录音失败: {e}")
    
    def stop_recording(self) -> bytes:
        """停止录音
        
        Returns:
            录音的音频数据
        """
        if not self.is_recording:
            raise ASRRecordingError("当前没有在录音")
        
        try:
            self.is_recording = False
            
            # 等待录音线程结束
            if self.record_thread:
                self.record_thread.join(timeout=2)
                if self.record_thread.is_alive():
                    raise ASRRecordingError("录音线程未能正常结束")
            
            # 获取音频数据
            audio_data = b''.join(self.frames)
            
            # 清理资源
            self._cleanup_audio()
            
            return audio_data
            
        except Exception as e:
            self._cleanup_audio()
            if isinstance(e, ASRRecordingError):
                raise
            else:
                raise ASRRecordingError(f"停止录音失败: {e}")
    
    def save_audio_to_file(self, audio_data: bytes, file_path: str):
        """保存音频数据到文件
        
        Args:
            audio_data: 音频数据
            file_path: 文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(self.config.format_bits // 8)
                wf.setframerate(self.config.rate)
                wf.writeframes(audio_data)
                
        except Exception as e:
            raise ASRAudioError(f"保存音频文件失败: {e}", file_path=file_path)
    
    def record_for_duration(self, duration: float) -> bytes:
        """录音指定时长
        
        Args:
            duration: 录音时长（秒）
            
        Returns:
            录音的音频数据
        """
        if duration <= 0:
            raise ValueError("录音时长必须大于0")
        
        self.start_recording()
        
        try:
            time.sleep(duration)
            return self.stop_recording()
        except Exception:
            if self.is_recording:
                self.is_recording = False
                self._cleanup_audio()
            raise
    
    def get_recording_info(self) -> Dict[str, Any]:
        """获取当前录音信息
        
        Returns:
            录音信息字典
        """
        return {
            'is_recording': self.is_recording,
            'duration': len(self.frames) * self.config.chunk / self.config.rate if self.frames else 0,
            'frames_count': len(self.frames),
            'config': {
                'rate': self.config.rate,
                'channels': self.config.channels,
                'chunk': self.config.chunk,
                'format_bits': self.config.format_bits,
                'device_index': self.config.device_index
            }
        }
    
    def __del__(self):
        """析构函数，清理资源"""
        if self.is_recording:
            self.is_recording = False
        self._cleanup_audio()