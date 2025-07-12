"""TTS工具模块"""
import time
import wave
import os
from typing import List, Optional
import numpy as np

def generate_request_id(prefix: str = "req") -> str:
    """生成请求ID"""
    timestamp = int(time.time() * 1000)
    return f"{prefix}_{timestamp}"

def save_audio_to_file(audio_data: bytes, filename: str, 
                      channels: int = 1, sample_width: int = 2, 
                      frame_rate: int = 44100) -> bool:
    """保存音频数据到WAV文件"""
    try:
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(frame_rate)
            wav_file.writeframes(audio_data)
        return True
    except Exception as e:
        print(f"保存音频文件失败: {e}")
        return False

def load_audio_from_file(filename: str) -> Optional[tuple]:
    """从WAV文件加载音频数据
    
    Returns:
        tuple: (audio_data, channels, sample_width, frame_rate) 或 None
    """
    try:
        with wave.open(filename, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            audio_data = wav_file.readframes(-1)
            return audio_data, channels, sample_width, frame_rate
    except Exception as e:
        print(f"加载音频文件失败: {e}")
        return None

def calculate_audio_duration(audio_data: bytes, sample_rate: int = 44100, 
                           sample_width: int = 2, channels: int = 1) -> float:
    """计算音频时长（秒）"""
    try:
        num_samples = len(audio_data) // (sample_width * channels)
        duration = num_samples / sample_rate
        return duration
    except:
        return 0.0

def convert_audio_format(audio_data: bytes, from_rate: int, to_rate: int,
                        from_channels: int = 1, to_channels: int = 1) -> bytes:
    """转换音频格式（简单重采样）
    
    注意：这是一个简单的实现，实际应用中建议使用专业的音频处理库
    """
    try:
        # 将字节数据转换为numpy数组
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # 简单的线性插值重采样
        if from_rate != to_rate:
            ratio = to_rate / from_rate
            new_length = int(len(audio_array) * ratio)
            indices = np.linspace(0, len(audio_array) - 1, new_length)
            audio_array = np.interp(indices, np.arange(len(audio_array)), audio_array)
            audio_array = audio_array.astype(np.int16)
        
        # 声道转换（简单处理）
        if from_channels != to_channels:
            if from_channels == 1 and to_channels == 2:
                # 单声道转立体声
                audio_array = np.repeat(audio_array, 2)
            elif from_channels == 2 and to_channels == 1:
                # 立体声转单声道
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
        
        return audio_array.tobytes()
    except Exception as e:
        print(f"音频格式转换失败: {e}")
        return audio_data

def validate_audio_config(format_type: int, channels: int, rate: int, chunk: int) -> bool:
    """验证音频配置参数"""
    # 检查格式
    valid_formats = [8, 16, 24, 32]  # 简化的格式检查
    
    # 检查声道数
    if channels not in [1, 2]:
        return False
    
    # 检查采样率
    valid_rates = [8000, 16000, 22050, 44100, 48000, 96000]
    if rate not in valid_rates:
        return False
    
    # 检查块大小
    if chunk <= 0 or chunk > 8192:
        return False
    
    return True

def format_duration(seconds: float) -> str:
    """格式化时长显示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}分{secs:.1f}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}小时{minutes}分{secs:.1f}秒"

def get_file_size_mb(filepath: str) -> float:
    """获取文件大小（MB）"""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0