#!/usr/bin/env python3
"""
实时语音对话系统

基于ASR+CHAT+TTS的实时语音交互系统，支持：
- 手动控制录音（按回车开始/停止）
- 智能对话
- 流式语音合成
- TTS播放打断功能
"""

import threading
import time
import queue
import numpy as np
import pyaudio
from typing import Optional, Callable
from pathlib import Path
import sys
import tempfile
import os

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入项目模块
from asr import StreamingASR
from chat import ChatBot
from tts import StreamingTTS



class RealtimeVoiceChat:
    """实时语音对话系统"""
    
    def __init__(self, 
                 chunk_size: int = 1024,
                 sample_rate: int = 44100):
        """
        初始化实时语音对话系统
        
        Args:
            chunk_size: 音频块大小
            sample_rate: 采样率
        """
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        
        # 初始化模块
        self.asr = None
        self.chatbot = None
        self.tts = None
        self._init_modules()
        
        # 音频录制相关
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_buffer = queue.Queue()
        self.recording_buffer = []
        
        # 控制标志
        self.is_running = False
        self.is_recording = False  # 手动录音状态
        self.is_processing = False
        
        # 线程
        self.audio_thread = None
        
        # 回调函数
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_end: Optional[Callable] = None
        self.on_user_text: Optional[Callable[[str], None]] = None
        self.on_assistant_text: Optional[Callable[[str], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None
    
    def _init_modules(self):
        """初始化ASR、CHAT、TTS模块"""
        try:
            print("🔧 正在初始化模块...")
            
            # 初始化ASR
            self.asr = StreamingASR.from_env()
            print("✅ ASR模块初始化成功")
            
            # 初始化ChatBot
            self.chatbot = ChatBot()
            print("✅ Chat模块初始化成功")
            
            # 初始化TTS
            from tts.env_config import load_from_env
            tts_config = load_from_env()
            self.tts = StreamingTTS(tts_config)
            print("✅ TTS模块初始化成功")
            
            print("🎉 所有模块初始化完成")
            
        except Exception as e:
            print(f"❌ 模块初始化失败: {e}")
            raise
    
    def _update_status(self, status: str):
        """更新状态"""
        print(f"📊 状态: {status}")
        if self.on_status_change:
            self.on_status_change(status)
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        if self.is_recording and not self.is_processing:
            self.recording_buffer.append(in_data)
        return (None, pyaudio.paContinue)
    
    def start_recording(self):
        """开始录音"""
        if self.is_processing:
            print("⚠️ 系统正在处理中，请稍后")
            return False
            
        if self.is_recording:
            print("⚠️ 已在录音中")
            return False
            
        # 打断TTS播放
        if self.tts.is_playing():
            self.tts.stop_current_playback()
            self._update_status("🛑 已打断TTS播放")
            
        self.recording_buffer = []
        self.is_recording = True
        self._update_status("🎤 开始录音...")
        
        if self.on_recording_start:
            self.on_recording_start()
            
        return True
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            print("⚠️ 当前未在录音")
            return False
            
        self.is_recording = False
        self._update_status("⏹️ 录音结束，开始处理...")
        
        if self.on_recording_end:
            self.on_recording_end()
            
        # 处理录音
        if self.recording_buffer:
            threading.Thread(target=self._process_recording, daemon=True).start()
        else:
            self._update_status("⚠️ 未录制到音频数据")
            
        return True
    
    def _process_recording(self):
        """处理录音数据"""
        if not self.recording_buffer:
            return
        
        try:
            self.is_processing = True
            
            # 合并音频数据
            audio_data = b''.join(self.recording_buffer)
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                # 写入WAV文件头
                import wave
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data)
                
                tmp_file_path = tmp_file.name
            
            # ASR转录
            self._update_status("🔄 正在识别语音...")
            text = self.asr.transcribe_audio(tmp_file_path)
            
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            
            if not text.strip():
                self._update_status("⚠️ 未识别到有效语音")
                return
            
            print(f"👤 用户: {text}")
            if self.on_user_text:
                self.on_user_text(text)
            
            # 获取AI回复
            self._update_status("🤖 AI正在思考...")
            response = self.chatbot.chat(text)
            
            print(f"🤖 助手: {response}")
            if self.on_assistant_text:
                self.on_assistant_text(response)
            
            # TTS播放
            self._update_status("🔊 正在合成语音...")
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            self._update_status("⏸️ 系统就绪，按回车开始录音")
            
        except Exception as e:
            print(f"❌ 处理录音失败: {e}")
            self._update_status(f"❌ 处理失败: {e}")
        finally:
            self.is_processing = False
    
    def start(self):
        """启动实时语音对话系统"""
        if self.is_running:
            print("⚠️ 系统已在运行中")
            return
        
        try:
            print("🚀 启动实时语音对话系统...")
            
            # 初始化音频流
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_running = True
            
            # 启动音频流
            self.stream.start_stream()
            
            self._update_status("⏸️ 系统就绪，按回车开始录音")
            print("✅ 系统启动成功！")
            print("💡 按回车开始录音，再按回车停止录音")
            print("💡 按回车可以中断TTS播放")
            print("💡 按 Ctrl+C 退出系统")
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            self.stop()
            raise
    
    def stop(self):
        """停止实时语音对话系统"""
        print("🛑 正在停止系统...")
        
        self.is_running = False
        self.is_recording = False
        
        # 停止TTS播放
        if self.tts:
            self.tts.stop_current_playback()
        
        # 停止音频流
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # 关闭PyAudio
        if self.audio:
            self.audio.terminate()
        
        print("✅ 系统已停止")
    
    def toggle_recording(self):
        """切换录音状态"""
        if self.is_recording:
            return self.stop_recording()
        else:
            return self.start_recording()
    
    def interrupt_tts(self):
        """手动打断TTS播放"""
        if self.tts.is_playing():
            self.tts.stop_current_playback()
            self._update_status("🛑 已手动打断TTS播放")
            print("🛑 已手动打断TTS播放")
        else:
            print("ℹ️ 当前没有TTS播放")
    
    def send_text_message(self, text: str):
        """发送文本消息"""
        if self.is_processing:
            print("⚠️ 系统正在处理中，请稍后")
            return
        
        try:
            self.is_processing = True
            
            # 打断TTS播放
            if self.tts.is_playing():
                self.tts.stop_current_playback()
            
            print(f"👤 用户: {text}")
            if self.on_user_text:
                self.on_user_text(text)
            
            # 获取AI回复
            self._update_status("🤖 AI正在思考...")
            response = self.chatbot.chat(text)
            
            print(f"🤖 助手: {response}")
            if self.on_assistant_text:
                self.on_assistant_text(response)
            
            # TTS播放
            self._update_status("🔊 正在合成语音...")
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            self._update_status("⏸️ 系统就绪，按回车开始录音")
            
        except Exception as e:
            print(f"❌ 处理文本消息失败: {e}")
            self._update_status(f"❌ 处理失败: {e}")
        finally:
            self.is_processing = False

def main():
    """主函数"""
    # 创建实时语音对话系统
    chat_system = RealtimeVoiceChat(
        chunk_size=1024,  # 音频块大小
        sample_rate=44100  # 采样率
    )
    
    # 设置回调函数
    def on_user_text(text):
        print(f"📝 识别到用户语音: {text}")
    
    def on_assistant_text(text):
        print(f"💬 AI回复: {text}")
    
    def on_status_change(status):
        print(f"🔄 状态变化: {status}")
    
    def on_recording_start():
        print("🎤 开始录音...")
    
    def on_recording_end():
        print("⏹️ 录音结束")
    
    chat_system.on_user_text = on_user_text
    chat_system.on_assistant_text = on_assistant_text
    chat_system.on_status_change = on_status_change
    chat_system.on_recording_start = on_recording_start
    chat_system.on_recording_end = on_recording_end
    
    try:
        # 启动系统
        chat_system.start()
        
        # 主循环
        print("\n🎯 使用说明:")
        print("  - 按回车开始录音，再按回车停止录音")
        print("  - 按回车可以中断TTS播放")
        print("  - 输入文本进行文字对话")
        print("  - 输入 'quit' 退出系统\n")
        
        while chat_system.is_running:
            try:
                user_input = input().strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input == '':
                    # 回车键：切换录音状态或中断TTS
                    if chat_system.tts.is_playing():
                        chat_system.interrupt_tts()
                    else:
                        chat_system.toggle_recording()
                else:
                    # 文本输入：进行文字对话
                    chat_system.send_text_message(user_input)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"❌ 系统错误: {e}")
    finally:
        chat_system.stop()
        print("👋 再见！")

if __name__ == "__main__":
    main()