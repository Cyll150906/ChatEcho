#!/usr/bin/env python3
"""
Web版实时语音对话系统

基于Flask的Web界面，模仿GPT-4o交互方式
支持点击小球进行语音对话和打断TTS播放
"""

import os
import sys
import threading
import time
import tempfile
import wave
import base64
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入项目模块
from asr import StreamingASR
from chat import ChatBot
from tts import StreamingTTS
from tts.env_config import load_from_env

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
chat_sessions = {}

class WebVoiceChat:
    """Web版语音对话系统"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.is_recording = False
        self.is_processing = False
        
        # 初始化模块
        self.asr = StreamingASR.from_env()
        self.chatbot = ChatBot()
        tts_config = load_from_env()
        self.tts = StreamingTTS(tts_config)
        
        print(f"✅ 会话 {session_id} 初始化完成")
    
    def start_recording(self):
        """开始录音"""
        if self.is_processing:
            return {'success': False, 'message': '系统正在处理中，请稍后'}
            
        if self.is_recording:
            return {'success': False, 'message': '已在录音中'}
            
        # 打断TTS播放
        if self.tts.is_playing():
            self.tts.stop_current_playback()
            self._emit_status('🛑 已打断TTS播放')
            
        self.is_recording = True
        self._emit_status('🎤 开始录音...')
        return {'success': True, 'message': '开始录音'}
    
    def stop_recording(self, audio_data: bytes):
        """停止录音并处理"""
        if not self.is_recording:
            return {'success': False, 'message': '当前未在录音'}
            
        self.is_recording = False
        self._emit_status('⏹️ 录音结束，开始处理...')
        
        # 异步处理录音
        threading.Thread(target=self._process_audio, args=(audio_data,), daemon=True).start()
        return {'success': True, 'message': '录音结束'}
    
    def interrupt_tts(self):
        """打断TTS播放"""
        if self.tts.is_playing():
            self.tts.stop_current_playback()
            self._emit_status('🛑 已打断TTS播放')
            return {'success': True, 'message': '已打断TTS播放'}
        else:
            return {'success': False, 'message': '当前没有TTS播放'}
    
    def send_text_message(self, text: str):
        """发送文本消息"""
        if self.is_processing:
            return {'success': False, 'message': '系统正在处理中，请稍后'}
            
        # 打断TTS播放
        if self.tts.is_playing():
            self.tts.stop_current_playback()
            
        # 异步处理文本
        threading.Thread(target=self._process_text, args=(text,), daemon=True).start()
        return {'success': True, 'message': '开始处理文本'}
    
    def _process_audio(self, audio_data: bytes):
        """处理音频数据"""
        try:
            self.is_processing = True
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # ASR转录
            self._emit_status('🔄 正在识别语音...')
            text = self.asr.transcribe_audio(tmp_file_path)
            
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            
            if not text.strip():
                self._emit_status('⚠️ 未识别到有效语音')
                return
            
            self._emit_user_message(text)
            
            # 获取AI回复
            self._emit_status('🤖 AI正在思考...')
            response = self.chatbot.chat(text)
            
            self._emit_assistant_message(response)
            
            # TTS播放
            self._emit_status('🔊 正在合成语音...')
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            self._emit_status('⏸️ 系统就绪，点击小球开始对话')
            
        except Exception as e:
            print(f"❌ 处理音频失败: {e}")
            self._emit_status(f'❌ 处理失败: {e}')
        finally:
            self.is_processing = False
    
    def _process_text(self, text: str):
        """处理文本消息"""
        try:
            self.is_processing = True
            
            self._emit_user_message(text)
            
            # 获取AI回复
            self._emit_status('🤖 AI正在思考...')
            response = self.chatbot.chat(text)
            
            self._emit_assistant_message(response)
            
            # TTS播放
            self._emit_status('🔊 正在合成语音...')
            self.tts.send_tts_request(response)
            
            # 等待播放完成
            self.tts.wait_for_completion()
            
            self._emit_status('⏸️ 系统就绪，点击小球开始对话')
            
        except Exception as e:
            print(f"❌ 处理文本失败: {e}")
            self._emit_status(f'❌ 处理失败: {e}')
        finally:
            self.is_processing = False
    
    def _emit_status(self, status: str):
        """发送状态更新"""
        socketio.emit('status_update', {'status': status}, room=self.session_id)
    
    def _emit_user_message(self, text: str):
        """发送用户消息"""
        socketio.emit('user_message', {'text': text}, room=self.session_id)
    
    def _emit_assistant_message(self, text: str):
        """发送助手消息"""
        socketio.emit('assistant_message', {'text': text}, room=self.session_id)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    # 创建新的聊天会话
    chat_sessions[session_id] = WebVoiceChat(session_id)
    
    # 加入房间
    from flask_socketio import join_room
    join_room(session_id)
    
    emit('connected', {'session_id': session_id})
    emit('status_update', {'status': '⏸️ 系统就绪，点击小球开始对话'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        del chat_sessions[session_id]
        print(f"🗑️ 会话 {session_id} 已清理")

@socketio.on('start_recording')
def handle_start_recording():
    """开始录音"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        result = chat_sessions[session_id].start_recording()
        emit('recording_response', result)

@socketio.on('stop_recording')
def handle_stop_recording(data):
    """停止录音"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        # 解码音频数据
        audio_data = base64.b64decode(data['audio_data'])
        result = chat_sessions[session_id].stop_recording(audio_data)
        emit('recording_response', result)

@socketio.on('interrupt_tts')
def handle_interrupt_tts():
    """打断TTS"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        result = chat_sessions[session_id].interrupt_tts()
        emit('interrupt_response', result)

@socketio.on('send_text')
def handle_send_text(data):
    """发送文本消息"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        text = data.get('text', '').strip()
        if text:
            result = chat_sessions[session_id].send_text_message(text)
            emit('text_response', result)

if __name__ == '__main__':
    # 创建模板目录
    template_dir = Path(__file__).parent / 'templates'
    template_dir.mkdir(exist_ok=True)
    
    print("🚀 启动Web语音对话系统...")
    print("📱 访问地址: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)