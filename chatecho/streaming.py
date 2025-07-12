import os
import requests
import pyaudio
import threading
import time
import struct
import queue
from typing import Optional
import numpy as np
import pydub

class StreamingTTS:
    def __init__(self):
        # 初始化PyAudio
        self.p = pyaudio.PyAudio()
        
        # 音频参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # 单声道
        self.RATE = 44100
        self.CHUNK = 2048
        
        # 创建音频输出流
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK
        )
        
        # 音频队列用于缓冲多个请求的音频数据
        self.audio_queue = queue.Queue()
        
        # 播放线程控制
        self.playing = False
        self.stop_playing = False
        self.interrupt_playing = False  # 新增：用于打断当前播放
        self.paused = False  # 新增：用于暂停播放
        self.pause_lock = threading.Lock()  # 暂停锁
        
        # 启动音频播放线程
        self.play_thread = threading.Thread(target=self._audio_player, daemon=True)
        self.play_thread.start()
        
        # 流式TTS系统已初始化
    
    def _parse_wav_header(self, data):
        """解析WAV文件头，返回音频数据开始位置"""
        try:
            if len(data) < 44:  # WAV头至少44字节
                return None
            
            # 检查RIFF标识
            if data[:4] != b'RIFF':
                return None
            
            # 检查WAVE标识
            if data[8:12] != b'WAVE':
                return None
            
            # 查找data chunk
            pos = 12
            while pos < len(data) - 8:
                chunk_id = data[pos:pos+4]
                chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                
                if chunk_id == b'data':
                    return pos + 8  # 返回音频数据开始位置
                
                pos += 8 + chunk_size
            
            return None
        except:
            return None
    
    def _audio_player(self):
        """音频播放线程，从队列中取出音频数据并播放"""
        while not self.stop_playing:
            try:
                # 检查是否需要打断播放
                if self.interrupt_playing:
                    # 清空音频队列
                    while not self.audio_queue.empty():
                        try:
                            self.audio_queue.get_nowait()
                            self.audio_queue.task_done()
                        except queue.Empty:
                            break
                    self.interrupt_playing = False
                    self.playing = False
                    continue
                
                # 检查是否暂停
                with self.pause_lock:
                    if self.paused:
                        self.playing = False
                        time.sleep(0.1)  # 暂停时短暂休眠
                        continue
                
                # 从队列中获取音频数据，超时1秒
                audio_chunk = self.audio_queue.get(timeout=1.0)
                
                if audio_chunk is None:  # 结束信号
                    break
                
                # 播放音频块
                self.playing = True
                self.stream.write(audio_chunk)
                self.audio_queue.task_done()
                
            except queue.Empty:
                self.playing = False
                continue
            except Exception as e:
                print(f"播放音频时出错: {e}")
    
    def _process_stream_response(self, response, request_id):
        """处理单个流式响应"""
        audio_buffer = bytearray()
        wav_header_parsed = False
        
        # 开始接收音频数据
        
        try:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_buffer.extend(chunk)
                    
                    # 如果还没有解析WAV头
                    if not wav_header_parsed and len(audio_buffer) >= 44:
                        data_start = self._parse_wav_header(audio_buffer)
                        if data_start is not None:
                            wav_header_parsed = True
                            # WAV头解析成功
                            # 移除WAV头，只保留音频数据
                            audio_buffer = audio_buffer[data_start:]
                    
                    # 如果有足够的音频数据且已解析头部
                    if wav_header_parsed and len(audio_buffer) >= self.CHUNK * 2:
                        # 取出音频数据块放入播放队列
                        while len(audio_buffer) >= self.CHUNK * 2:
                            chunk_size = self.CHUNK * 2
                            audio_chunk = bytes(audio_buffer[:chunk_size])
                            audio_buffer = audio_buffer[chunk_size:]
                            
                            # 将音频块加入播放队列
                            self.audio_queue.put(audio_chunk)
                            # 添加音频块到播放队列
            
            # 处理剩余的音频数据
            if wav_header_parsed and len(audio_buffer) > 0:
                self.audio_queue.put(bytes(audio_buffer))
                # 添加最后的音频块
            
            # 音频数据接收完成
            
        except Exception as e:
            print(f"处理流式响应时出错: {e}")
    
    def send_tts_request(self, text: str, request_id: Optional[str] = None):
        """发送TTS请求并开始流式播放"""
        if request_id is None:
            request_id = f"req_{int(time.time() * 1000)}"
        
        url = "https://api.siliconflow.cn/v1/audio/speech"
        
        payload = {
            "input": text,
            "response_format": "wav",
            "sample_rate": 44100,
            "stream": True,
            "speed": 1,
            "gain": 0,
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "voice": "FunAudioLLM/CosyVoice2-0.5B:anna"
        }
        
        headers = {
            "Authorization": "Bearer sk-oyxoqrxbymcizdfmfuzdxtudualgftadigummmozhhpdjamu",
            "Content-Type": "application/json"
        }
        
        # 发送TTS请求
        
        try:
            # 发送请求
            response = requests.post(url, json=payload, headers=headers, stream=True)
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
    
    def stop_current_playback(self):
        """停止当前播放并清空音频队列"""
        self.interrupt_playing = True
        print("🛑 已打断语音播放")
    
    def is_playing(self):
        """检查是否正在播放音频"""
        return self.playing or not self.audio_queue.empty()
    
    def wait_for_completion(self):
        """等待所有音频播放完成"""
        # 等待所有音频播放完成
        self.audio_queue.join()
        # 所有音频播放完成
    
    def close(self):
        """关闭TTS系统"""
        # 正在关闭TTS系统
        
        # 停止播放线程
        self.stop_playing = True
        self.audio_queue.put(None)  # 发送结束信号
        
        # 等待播放线程结束
        if self.play_thread.is_alive():
            self.play_thread.join(timeout=2.0)
        
        # 关闭音频流
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        
        # 终止PyAudio
        if hasattr(self, 'p'):
            self.p.terminate()
        
        # TTS系统已关闭

# 使用示例
if __name__ == "__main__":
    # 创建流式TTS实例
    tts = StreamingTTS()
    
    try:
        # 发送多个TTS请求
        texts = [
            "这是第一段测试文本，用于验证流式播放功能。",
            "这是第二段测试文本，应该在第一段播放的同时开始处理。",
            "这是第三段测试文本，展示了并发处理的能力。"
        ]
        
        # 导入所需的库
        import matplotlib.pyplot as plt
        import numpy as np
        import wave
        import os
        import pydub
        
        # 设置中文字体显示
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 停止播放功能，只收集音频数据
        tts.stop_playing = True
        
        audio_files = []
        
        # 为每个语音生成音频文件
        for i, text in enumerate(texts, 1):
            # 发送TTS请求
            request_id = tts.send_tts_request(text, f"test_{i}")
            
            # 收集当前语音的音频数据
            audio_data = []
            
            # 等待音频数据积累（不播放）
            import time
            time.sleep(3)  # 等待音频数据生成
            
            # 收集所有音频数据
            while not tts.audio_queue.empty():
                chunk = tts.audio_queue.get()
                if chunk is not None:
                    audio_data.extend(chunk)
                    
            # 保存音频文件
            if audio_data:
                filename = f"generated_audio_{i}.wav"
                with wave.open(filename, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # 单声道
                    wav_file.setsampwidth(2)  # 16位
                    wav_file.setframerate(44100)  # 采样率
                    wav_file.writeframes(bytes(audio_data))
                audio_files.append(filename)
                print(f"已保存音频文件: {filename}")
        
        # 创建拼接的波形图
        plt.figure(figsize=(16, 12))
        
        # 处理现有的a.m4a文件（如果存在且可以处理）
        plot_index = 1
        if os.path.exists("a.m4a"):
            try:
                audio = pydub.AudioSegment.from_file("a.m4a", format="m4a")
                samples = np.array(audio.get_array_of_samples())
                
                plt.subplot(len(audio_files) + 1, 1, plot_index)
                plt.plot(samples)
                plt.title("原始音频 (a.m4a)")
                plt.xlabel("采样点")
                plt.ylabel("振幅")
                plt.grid(True)
                plot_index += 1
                print("已添加原始音频 a.m4a 到波形图")
            except Exception as e:
                print(f"无法处理 a.m4a 文件 (需要安装ffmpeg): {e}")
                print("跳过 a.m4a 文件，仅显示生成的音频文件")
        
        # 处理生成的WAV文件
        for i, audio_file in enumerate(audio_files, 1):
            plt.subplot(len(audio_files) + (1 if os.path.exists("a.m4a") and plot_index > 1 else 0), 1, plot_index)
            
            try:
                with wave.open(audio_file, 'rb') as wav_file:
                    frames = wav_file.readframes(-1)
                    samples = np.frombuffer(frames, dtype=np.int16)
                
                # 绘制波形图
                plt.plot(samples)
                plt.title(f"生成音频 {i}")
                plt.xlabel("采样点")
                plt.ylabel("振幅")
                plt.grid(True)
                plot_index += 1
            except Exception as e:
                print(f"无法读取音频文件 {audio_file}: {e}")
        
        plt.tight_layout()
        plt.show()
        
        print(f"已生成包含 {len(audio_files)} 个音频的拼接波形图")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        # 关闭TTS系统
        tts.close()