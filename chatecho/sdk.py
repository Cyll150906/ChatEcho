import pyaudio
import wave
import requests
import threading
import time
import os
import pyaudio
from datetime import datetime
from config import Config, get_api_key

class VoiceToTextSDK:
    """录音转文字SDK，提供简单的函数调用接口"""
    
    def __init__(self, api_key=None, audio_device_index=None):
        """
        初始化SDK
        
        Args:
            api_key (str, optional): SiliconFlow API密钥，如果不提供则使用全局配置
            audio_device_index (int, optional): 音频设备索引
        """
        self.api_key = api_key or Config.get_api_key()
        self.api_url = Config.get_api_url()
        self.model_name = Config.get_model_name()
        
        # 录音参数
        self.chunk = Config.AUDIO_CHUNK
        self.format = pyaudio.paInt16
        self.channels = Config.AUDIO_CHANNELS
        self.rate = Config.AUDIO_RATE
        self.audio_device_index = audio_device_index
        
        self.audio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        
    def _init_audio(self):
        """初始化音频设备"""
        if self.audio is None:
            self.audio = pyaudio.PyAudio()
    
    def _cleanup_audio(self):
        """清理音频资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
    
    def start_recording(self):
        """
        开始录音
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if self.is_recording:
                print("⚠️ 已经在录音中")
                return False
                
            self._init_audio()
            
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.frames = []
            self.is_recording = True
            
            def record_audio():
                while self.is_recording:
                    try:
                        data = self.stream.read(self.chunk)
                        self.frames.append(data)
                    except Exception as e:
                        print(f"录音过程中出错: {e}")
                        break
            
            self.record_thread = threading.Thread(target=record_audio)
            self.record_thread.daemon = True
            self.record_thread.start()
            
            print("🎤 开始录音...")
            return True
            
        except Exception as e:
            print(f"❌ 开始录音失败: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self):
        """
        停止录音
        
        Returns:
            str: 录音文件路径，失败返回None
        """
        try:
            if not self.is_recording:
                print("⚠️ 当前没有在录音")
                return None
            
            self.is_recording = False
            
            # 等待录音线程结束
            if hasattr(self, 'record_thread'):
                self.record_thread.join(timeout=1)
            
            print("🛑 停止录音")
            
            # 保存录音文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = Config.get_temp_dir()
            filename = os.path.join(temp_dir, f"recording_{timestamp}.wav")
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            
            self._cleanup_audio()
            
            print(f"💾 录音已保存: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 停止录音失败: {e}")
            self._cleanup_audio()
            return None
    
    def transcribe_audio(self, audio_file_path):
        """
        将音频文件转换为文字
        
        Args:
            audio_file_path (str): 音频文件路径
            
        Returns:
            str: 转换后的文字，失败返回None
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"❌ 音频文件不存在: {audio_file_path}")
                return None
            
            print("🔄 正在转换为文字...")
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
                }
                
                data = {
                    'model': self.model_name
                }
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=Config.get_api_timeout()
                )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                if text:
                    print(f"✅ 转换成功: {text}")
                    return text
                else:
                    print("⚠️ 转换结果为空")
                    return None
            else:
                print(f"❌ API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return None
    
    def record_and_transcribe(self, duration=None, auto_delete=True):
        """
        录音并转换为文字（一键完成）
        
        Args:
            duration (int, optional): 录音时长（秒），None表示手动停止
            auto_delete (bool): 是否自动删除录音文件
            
        Returns:
            str: 转换后的文字，失败返回None
        """
        try:
            # 开始录音
            if not self.start_recording():
                return None
            
            if duration:
                # 自动录音指定时长
                print(f"⏱️ 将录音 {duration} 秒...")
                time.sleep(duration)
            else:
                # 手动停止录音
                input("按 Enter 键停止录音...")
            
            # 停止录音
            audio_file = self.stop_recording()
            if not audio_file:
                return None
            
            # 转换为文字
            text = self.transcribe_audio(audio_file)
            
            # 删除录音文件
            if auto_delete and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                    print(f"🗑️ 已删除录音文件: {audio_file}")
                except Exception as e:
                    print(f"⚠️ 删除录音文件失败: {e}")
            
            return text
            
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断录音")
            if self.is_recording:
                self.stop_recording()
            return None
        except Exception as e:
            print(f"❌ 录音转文字失败: {e}")
            return None
    
    def transcribe_file(self, file_path, auto_delete=False):
        """
        转换已有音频文件为文字
        
        Args:
            file_path (str): 音频文件路径
            auto_delete (bool): 是否自动删除音频文件
            
        Returns:
            str: 转换后的文字，失败返回None
        """
        text = self.transcribe_audio(file_path)
        
        if auto_delete and text and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ 已删除音频文件: {file_path}")
            except Exception as e:
                print(f"⚠️ 删除音频文件失败: {e}")
        
        return text
    
    def __del__(self):
        """析构函数，清理资源"""
        self._cleanup_audio()