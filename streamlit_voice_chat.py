#!/usr/bin/env python3
"""
Streamlit语音交互聊天系统

整合ASR、CHAT、TTS模块，提供完整的语音交互体验。
"""

import streamlit as st
import tempfile
import os
import time
from pathlib import Path
import threading
from typing import Optional

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

# 导入项目模块
from asr import StreamingASR
from chat import ChatBot
from tts import StreamingTTS

# 页面配置
st.set_page_config(
    page_title="ChatEcho - 语音交互聊天系统",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
}
.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
.user-message {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}
.assistant-message {
    background-color: #f3e5f5;
    border-left: 4px solid #9c27b0;
}
.status-box {
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.5rem 0;
    text-align: center;
}
.status-recording {
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ef5350;
}
.status-processing {
    background-color: #fff3e0;
    color: #ef6c00;
    border: 1px solid #ff9800;
}
.status-ready {
    background-color: #e8f5e8;
    color: #2e7d32;
    border: 1px solid #4caf50;
}
</style>
""", unsafe_allow_html=True)

class VoiceChatApp:
    """语音聊天应用主类"""
    
    def __init__(self):
        self.asr = None
        self.chatbot = None
        self.tts = None
        self.init_modules()
        
        # 初始化session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'is_recording' not in st.session_state:
            st.session_state.is_recording = False
        if 'current_status' not in st.session_state:
            st.session_state.current_status = "ready"
        if 'status_message' not in st.session_state:
            st.session_state.status_message = "系统就绪"
    
    def init_modules(self):
        """初始化ASR、CHAT、TTS模块"""
        try:
            # 初始化ASR
            self.asr = StreamingASR.from_env()
            
            # 初始化ChatBot
            self.chatbot = ChatBot()
            
            # 初始化TTS
            self.tts = StreamingTTS()
            
            st.success("✅ 所有模块初始化成功")
            
        except Exception as e:
            st.error(f"❌ 模块初始化失败: {e}")
            st.info("请检查.env文件配置是否正确")
    
    def update_status(self, status: str, message: str):
        """更新状态"""
        st.session_state.current_status = status
        st.session_state.status_message = message
    
    def display_status(self):
        """显示当前状态"""
        status_class = f"status-{st.session_state.current_status}"
        st.markdown(
            f'<div class="status-box {status_class}">{st.session_state.status_message}</div>',
            unsafe_allow_html=True
        )
    
    def display_chat_history(self):
        """显示聊天历史"""
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(
                    f'<div class="chat-message user-message"><strong>👤 用户:</strong><br>{message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>🤖 助手:</strong><br>{message["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    def process_voice_input(self, audio_file_path: str) -> Optional[str]:
        """处理语音输入"""
        try:
            # 打断当前TTS播放
            if self.tts.is_playing():
                self.tts.stop_current_playback()
            
            # 更新状态为处理中
            self.update_status("processing", "🔄 正在识别语音...")
            
            # ASR转录
            text = self.asr.transcribe_audio(audio_file_path)
            
            if not text.strip():
                self.update_status("ready", "⚠️ 未识别到有效语音")
                return None
            
            # 添加用户消息到历史
            st.session_state.chat_history.append({
                'role': 'user',
                'content': text
            })
            
            # 更新状态
            self.update_status("processing", "🤖 AI正在思考...")
            
            # 获取AI回复
            response = self.chatbot.chat(text)
            
            # 添加助手回复到历史
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # 更新状态
            self.update_status("processing", "🔊 正在合成语音...")
            
            # TTS播放回复
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            # 恢复就绪状态
            self.update_status("ready", "系统就绪")
            
            return text
            
        except Exception as e:
            self.update_status("ready", f"❌ 处理失败: {e}")
            st.error(f"处理语音输入时出错: {e}")
            return None
    
    def handle_text_input(self, text: str):
        """处理文本输入"""
        try:
            if not text.strip():
                return
            
            # 打断当前TTS播放
            if self.tts.is_playing():
                self.tts.stop_current_playback()
            
            # 添加用户消息到历史
            st.session_state.chat_history.append({
                'role': 'user',
                'content': text
            })
            
            # 更新状态
            self.update_status("processing", "🤖 AI正在思考...")
            
            # 获取AI回复
            response = self.chatbot.chat(text)
            
            # 添加助手回复到历史
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # 更新状态
            self.update_status("processing", "🔊 正在合成语音...")
            
            # TTS播放回复
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            # 恢复就绪状态
            self.update_status("ready", "系统就绪")
            
        except Exception as e:
            self.update_status("ready", f"❌ 处理失败: {e}")
            st.error(f"处理文本输入时出错: {e}")
    
    def run(self):
        """运行应用"""
        # 主标题
        st.markdown('<h1 class="main-header">🎤 ChatEcho - 语音交互聊天系统</h1>', unsafe_allow_html=True)
        
        # 检查模块是否初始化成功
        if not all([self.asr, self.chatbot, self.tts]):
            st.error("系统未正确初始化，请检查配置")
            return
        
        # 侧边栏控制面板
        with st.sidebar:
            st.header("🎛️ 控制面板")
            
            # 清空聊天历史
            if st.button("🗑️ 清空聊天历史", use_container_width=True):
                st.session_state.chat_history = []
                self.chatbot.clear_history()
                st.rerun()
            
            # 停止当前播放
            if st.button("⏹️ 停止语音播放", use_container_width=True):
                self.tts.stop_current_playback()
                self.update_status("ready", "系统就绪")
            
            st.divider()
            
            # 系统信息
            st.subheader("📊 系统信息")
            st.info(f"对话轮数: {len(st.session_state.chat_history)}")
            st.info(f"TTS状态: {'播放中' if self.tts.is_playing() else '空闲'}")
        
        # 主界面布局
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 显示状态
            self.display_status()
            
            # 聊天历史显示区域
            st.subheader("💬 对话历史")
            chat_container = st.container(height=400)
            with chat_container:
                self.display_chat_history()
        
        with col2:
            st.subheader("🎤 语音输入")
            
            # 音频录制器
            audio_bytes = st.audio_input("点击录音", key="voice_input")
            
            if audio_bytes is not None:
                # 保存音频到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes.getvalue())
                    tmp_file_path = tmp_file.name
                
                # 处理语音输入
                recognized_text = self.process_voice_input(tmp_file_path)
                
                # 清理临时文件
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                
                # 如果识别成功，重新运行以更新界面
                if recognized_text:
                    st.rerun()
            
            st.divider()
            
            # 文本输入
            st.subheader("⌨️ 文本输入")
            text_input = st.text_area(
                "输入消息",
                placeholder="在这里输入您的消息...",
                height=100,
                key="text_input"
            )
            
            if st.button("📤 发送", use_container_width=True):
                if text_input.strip():
                    self.handle_text_input(text_input)
                    st.rerun()
                else:
                    st.warning("请输入消息内容")

def main():
    """主函数"""
    app = VoiceChatApp()
    app.run()

if __name__ == "__main__":
    main()