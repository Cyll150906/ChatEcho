"""ASR工具模块

提供音频文件处理、临时文件管理等工具函数。
"""

import os
import wave
import tempfile
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

from .exceptions import ASRAudioError


def save_audio_to_file(audio_data: bytes, file_path: str, 
                      channels: int = 1, sample_width: int = 2, 
                      frame_rate: int = 44100):
    """保存音频数据到WAV文件
    
    Args:
        audio_data: 音频字节数据
        file_path: 保存路径
        channels: 声道数
        sample_width: 采样宽度（字节）
        frame_rate: 采样率
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(frame_rate)
            wf.writeframes(audio_data)
            
    except Exception as e:
        raise ASRAudioError(f"保存音频文件失败: {e}", file_path=file_path)


def load_audio_from_file(file_path: str) -> Tuple[bytes, dict]:
    """从WAV文件加载音频数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        (音频数据, 音频信息字典)
    """
    if not os.path.exists(file_path):
        raise ASRAudioError(f"音频文件不存在: {file_path}", file_path=file_path)
    
    try:
        with wave.open(file_path, 'rb') as wf:
            # 获取音频信息
            audio_info = {
                'channels': wf.getnchannels(),
                'sample_width': wf.getsampwidth(),
                'frame_rate': wf.getframerate(),
                'frames': wf.getnframes(),
                'duration': wf.getnframes() / wf.getframerate()
            }
            
            # 读取音频数据
            audio_data = wf.readframes(wf.getnframes())
            
            return audio_data, audio_info
            
    except Exception as e:
        raise ASRAudioError(f"加载音频文件失败: {e}", file_path=file_path)


def get_temp_filename(prefix: str = "asr_", suffix: str = ".wav", 
                     temp_dir: Optional[str] = None) -> str:
    """生成临时文件名
    
    Args:
        prefix: 文件名前缀
        suffix: 文件扩展名
        temp_dir: 临时目录，None表示使用系统默认
        
    Returns:
        临时文件路径
    """
    if temp_dir:
        os.makedirs(temp_dir, exist_ok=True)
        base_dir = temp_dir
    else:
        base_dir = tempfile.gettempdir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{prefix}{timestamp}{suffix}"
    
    return os.path.join(base_dir, filename)


def get_audio_info(file_path: str) -> dict:
    """获取音频文件信息
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        音频信息字典
    """
    if not os.path.exists(file_path):
        raise ASRAudioError(f"音频文件不存在: {file_path}", file_path=file_path)
    
    try:
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        info = {
            'file_path': file_path,
            'file_size': file_size,
            'file_size_mb': file_size / 1024 / 1024,
            'file_extension': file_ext,
            'is_wav': file_ext == '.wav'
        }
        
        # 如果是WAV文件，获取详细信息
        if file_ext == '.wav':
            try:
                with wave.open(file_path, 'rb') as wf:
                    info.update({
                        'channels': wf.getnchannels(),
                        'sample_width': wf.getsampwidth(),
                        'frame_rate': wf.getframerate(),
                        'frames': wf.getnframes(),
                        'duration': wf.getnframes() / wf.getframerate(),
                        'format_bits': wf.getsampwidth() * 8
                    })
            except Exception:
                info['wav_error'] = "无法读取WAV文件信息"
        
        return info
        
    except Exception as e:
        raise ASRAudioError(f"获取音频信息失败: {e}", file_path=file_path)


def validate_audio_file(file_path: str, max_size_mb: float = 25.0) -> bool:
    """验证音频文件是否有效
    
    Args:
        file_path: 音频文件路径
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        文件是否有效
    """
    try:
        info = get_audio_info(file_path)
        
        # 检查文件大小
        if info['file_size_mb'] > max_size_mb:
            return False
        
        # 检查文件格式
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm']
        if info['file_extension'] not in supported_formats:
            return False
        
        # 如果是WAV文件，检查格式参数
        if info['is_wav'] and 'channels' in info:
            if info['channels'] not in [1, 2]:
                return False
            if info['frame_rate'] < 8000 or info['frame_rate'] > 192000:
                return False
        
        return True
        
    except Exception:
        return False


def cleanup_temp_files(temp_dir: str, pattern: str = "asr_*.wav", 
                      max_age_hours: int = 24):
    """清理临时文件
    
    Args:
        temp_dir: 临时目录
        pattern: 文件名模式
        max_age_hours: 最大保留时间（小时）
    """
    try:
        import glob
        import time
        
        if not os.path.exists(temp_dir):
            return
        
        pattern_path = os.path.join(temp_dir, pattern)
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in glob.glob(pattern_path):
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
            except Exception:
                continue
                
    except Exception:
        pass


def convert_audio_format(input_path: str, output_path: str, 
                        target_rate: int = 44100, target_channels: int = 1):
    """转换音频格式（仅支持WAV文件）
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        target_rate: 目标采样率
        target_channels: 目标声道数
    """
    try:
        # 加载原始音频
        audio_data, info = load_audio_from_file(input_path)
        
        # 如果格式已经匹配，直接复制
        if (info['frame_rate'] == target_rate and 
            info['channels'] == target_channels):
            save_audio_to_file(
                audio_data, output_path,
                channels=info['channels'],
                sample_width=info['sample_width'],
                frame_rate=info['frame_rate']
            )
            return
        
        # 简单的格式转换（仅支持基本转换）
        if info['channels'] != target_channels:
            # 声道转换的简单实现
            if info['channels'] == 2 and target_channels == 1:
                # 立体声转单声道：取平均值
                import struct
                samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
                mono_samples = []
                for i in range(0, len(samples), 2):
                    if i + 1 < len(samples):
                        avg = (samples[i] + samples[i + 1]) // 2
                        mono_samples.append(avg)
                    else:
                        mono_samples.append(samples[i])
                audio_data = struct.pack(f'<{len(mono_samples)}h', *mono_samples)
            else:
                raise ASRAudioError("不支持的声道转换")
        
        # 采样率转换需要更复杂的算法，这里暂不实现
        if info['frame_rate'] != target_rate:
            raise ASRAudioError("不支持采样率转换，请使用专业音频处理库")
        
        # 保存转换后的音频
        save_audio_to_file(
            audio_data, output_path,
            channels=target_channels,
            sample_width=info['sample_width'],
            frame_rate=target_rate
        )
        
    except Exception as e:
        raise ASRAudioError(f"音频格式转换失败: {e}")


def estimate_transcription_time(file_path: str) -> float:
    """估算转录所需时间
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        估算的转录时间（秒）
    """
    try:
        info = get_audio_info(file_path)
        
        if 'duration' in info:
            # 基于经验：转录时间通常是音频时长的0.1-0.3倍
            base_time = info['duration'] * 0.2
            
            # 加上网络延迟和处理时间
            network_overhead = 2.0
            processing_overhead = info['file_size_mb'] * 0.5
            
            return base_time + network_overhead + processing_overhead
        else:
            # 如果无法获取时长，基于文件大小估算
            return info['file_size_mb'] * 2.0 + 5.0
            
    except Exception:
        return 30.0  # 默认估算30秒