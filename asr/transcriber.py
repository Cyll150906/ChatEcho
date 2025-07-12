"""ASR转录模块

封装语音转文字API调用逻辑，处理文件上传、请求发送、响应解析等功能。
"""

import requests
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

from .config import APIConfig
from .exceptions import ASRTranscriptionError, ASRAudioError


class SpeechTranscriber:
    """语音转录器
    
    提供语音转文字功能，支持文件上传、API调用、重试机制等。
    """
    
    def __init__(self, config: APIConfig):
        """初始化转录器
        
        Args:
            config: API配置
        """
        self.config = config
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Authorization': config.key,
            'User-Agent': 'ChatEcho-ASR/1.0.0'
        })
    
    def transcribe_file(self, file_path: str, **kwargs) -> str:
        """转录音频文件
        
        Args:
            file_path: 音频文件路径
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        if not os.path.exists(file_path):
            raise ASRAudioError(f"音频文件不存在: {file_path}", file_path=file_path)
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        max_size = 25 * 1024 * 1024  # 25MB
        if file_size > max_size:
            raise ASRAudioError(
                f"音频文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持25MB",
                file_path=file_path
            )
        
        # 检查文件格式
        file_ext = Path(file_path).suffix.lower()
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.webm']
        if file_ext not in supported_formats:
            raise ASRAudioError(
                f"不支持的音频格式: {file_ext}，支持的格式: {', '.join(supported_formats)}",
                file_path=file_path
            )
        
        # 执行转录
        return self._transcribe_with_retry(file_path, **kwargs)
    
    def transcribe_bytes(self, audio_data: bytes, filename: str = "audio.wav", **kwargs) -> str:
        """转录音频字节数据
        
        Args:
            audio_data: 音频字节数据
            filename: 文件名（用于API识别格式）
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        if not audio_data:
            raise ASRAudioError("音频数据为空")
        
        # 检查数据大小
        data_size = len(audio_data)
        max_size = 25 * 1024 * 1024  # 25MB
        if data_size > max_size:
            raise ASRAudioError(
                f"音频数据过大: {data_size / 1024 / 1024:.1f}MB，最大支持25MB"
            )
        
        return self._transcribe_bytes_with_retry(audio_data, filename, **kwargs)
    
    def _transcribe_with_retry(self, file_path: str, **kwargs) -> str:
        """带重试的文件转录
        
        Args:
            file_path: 音频文件路径
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return self._do_transcribe_file(file_path, **kwargs)
            except ASRTranscriptionError as e:
                last_exception = e
                
                # 某些错误不需要重试
                if e.status_code in [400, 401, 403, 413]:
                    raise
                
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception as e:
                last_exception = ASRTranscriptionError(f"转录失败: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise last_exception
        
        raise last_exception
    
    def _transcribe_bytes_with_retry(self, audio_data: bytes, filename: str, **kwargs) -> str:
        """带重试的字节数据转录
        
        Args:
            audio_data: 音频字节数据
            filename: 文件名
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return self._do_transcribe_bytes(audio_data, filename, **kwargs)
            except ASRTranscriptionError as e:
                last_exception = e
                
                # 某些错误不需要重试
                if e.status_code in [400, 401, 403, 413]:
                    raise
                
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception as e:
                last_exception = ASRTranscriptionError(f"转录失败: {e}")
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise last_exception
        
        raise last_exception
    
    def _do_transcribe_file(self, file_path: str, **kwargs) -> str:
        """执行文件转录
        
        Args:
            file_path: 音频文件路径
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        try:
            with open(file_path, 'rb') as audio_file:
                files = {
                    'file': (os.path.basename(file_path), audio_file, self._get_mime_type(file_path))
                }
                
                data = {
                    'model': self.config.model,
                    **kwargs
                }
                
                response = self.session.post(
                    self.config.url,
                    files=files,
                    data=data,
                    timeout=self.config.timeout
                )
                
                return self._parse_response(response)
                
        except requests.exceptions.Timeout:
            raise ASRTranscriptionError("API请求超时")
        except requests.exceptions.ConnectionError:
            raise ASRTranscriptionError("网络连接错误")
        except Exception as e:
            raise ASRTranscriptionError(f"转录请求失败: {e}")
    
    def _do_transcribe_bytes(self, audio_data: bytes, filename: str, **kwargs) -> str:
        """执行字节数据转录
        
        Args:
            audio_data: 音频字节数据
            filename: 文件名
            **kwargs: 额外的API参数
            
        Returns:
            转录结果文本
        """
        try:
            files = {
                'file': (filename, audio_data, self._get_mime_type_from_filename(filename))
            }
            
            data = {
                'model': self.config.model,
                **kwargs
            }
            
            response = self.session.post(
                self.config.url,
                files=files,
                data=data,
                timeout=self.config.timeout
            )
            
            return self._parse_response(response)
            
        except requests.exceptions.Timeout:
            raise ASRTranscriptionError("API请求超时")
        except requests.exceptions.ConnectionError:
            raise ASRTranscriptionError("网络连接错误")
        except Exception as e:
            raise ASRTranscriptionError(f"转录请求失败: {e}")
    
    def _parse_response(self, response: requests.Response) -> str:
        """解析API响应
        
        Args:
            response: HTTP响应对象
            
        Returns:
            转录结果文本
        """
        if response.status_code == 200:
            try:
                result = response.json()
                text = result.get('text', '').strip()
                
                if not text:
                    raise ASRTranscriptionError("转录结果为空")
                
                return text
                
            except ValueError as e:
                raise ASRTranscriptionError(
                    f"解析API响应失败: {e}",
                    status_code=response.status_code,
                    response_text=response.text
                )
        else:
            # 尝试解析错误信息
            error_msg = f"API调用失败: HTTP {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg += f" - {error_data['error']}"
                elif 'message' in error_data:
                    error_msg += f" - {error_data['message']}"
            except ValueError:
                error_msg += f" - {response.text}"
            
            raise ASRTranscriptionError(
                error_msg,
                status_code=response.status_code,
                response_text=response.text
            )
    
    def _get_mime_type(self, file_path: str) -> str:
        """根据文件路径获取MIME类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            MIME类型
        """
        return self._get_mime_type_from_filename(os.path.basename(file_path))
    
    def _get_mime_type_from_filename(self, filename: str) -> str:
        """根据文件名获取MIME类型
        
        Args:
            filename: 文件名
            
        Returns:
            MIME类型
        """
        ext = Path(filename).suffix.lower()
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm'
        }
        return mime_types.get(ext, 'audio/wav')
    
    def test_connection(self) -> bool:
        """测试API连接
        
        Returns:
            连接是否正常
        """
        try:
            # 发送一个简单的请求测试连接
            response = self.session.get(
                self.config.url.replace('/transcriptions', '/models'),
                timeout=5
            )
            return response.status_code in [200, 404]  # 404也表示连接正常
        except Exception:
            return False
    
    def get_supported_models(self) -> list:
        """获取支持的模型列表
        
        Returns:
            模型列表
        """
        try:
            response = self.session.get(
                self.config.url.replace('/transcriptions', '/models'),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return [model['id'] for model in data['data']]
            
            return [self.config.model]  # 返回默认模型
            
        except Exception:
            return [self.config.model]
    
    def __del__(self):
        """析构函数，关闭会话"""
        if hasattr(self, 'session'):
            self.session.close()