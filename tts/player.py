"""音频播放器模块"""
import pyaudio
import threading
import time
import queue

class AudioPlayer:
    """音频播放器类"""
    
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=44100, chunk=2048):
        """初始化音频播放器"""
        # 初始化PyAudio
        self.p = pyaudio.PyAudio()
        
        # 音频参数
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.CHUNK = chunk
        
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
        self.interrupt_playing = False  # 用于打断当前播放
        self.paused = False  # 用于暂停播放
        self.pause_lock = threading.Lock()  # 暂停锁
        
        # 启动音频播放线程
        self.play_thread = threading.Thread(target=self._audio_player, daemon=True)
        self.play_thread.start()
    
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
    
    def add_audio_chunk(self, audio_chunk):
        """添加音频块到播放队列"""
        self.audio_queue.put(audio_chunk)
    
    def stop_current_playback(self):
        """停止当前播放并清空音频队列"""
        self.interrupt_playing = True
        print("🛑 已打断语音播放")
    
    def pause(self):
        """暂停播放"""
        with self.pause_lock:
            self.paused = True
    
    def resume(self):
        """恢复播放"""
        with self.pause_lock:
            self.paused = False
    
    def is_playing(self):
        """检查是否正在播放音频"""
        return self.playing or not self.audio_queue.empty()
    
    def wait_for_completion(self):
        """等待所有音频播放完成"""
        self.audio_queue.join()
    
    def close(self):
        """关闭音频播放器"""
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