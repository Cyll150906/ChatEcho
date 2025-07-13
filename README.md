# ChatEcho - 语音处理系统

一个基于Python的语音处理系统，集成了文本转语音(TTS)、自动语音识别(ASR)和智能对话(Chat)功能。

## 🚀 功能特性

- **🎵 文本转语音(TTS)**: 流式音频播放，支持播放控制
- **🎤 语音识别(ASR)**: 音频文件转录，支持多种格式
- **🤖 智能对话(Chat)**: 支持函数调用的AI对话系统
- **🔧 模块化设计**: 清晰的架构，易于维护
- **🔒 安全配置**: 环境变量管理API密钥

## 📁 项目结构

```
ChatEcho/
├── tts/                    # TTS模块
├── asr/                    # ASR模块
├── chat/                   # Chat模块
├── .env.example            # 环境变量示例
├── requirements.txt        # 项目依赖
└── README.md              # 项目文档
```

## 🛠️ 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

## 🚀 快速开始

### 环境配置

编辑 `.env` 文件：

```bash
# TTS配置
TTS_API_KEY=sk-your-tts-api-key-here
TTS_API_URL=https://api.siliconflow.cn/v1/audio/speech
TTS_MODEL=FunAudioLLM/CosyVoice2-0.5B
TTS_VOICE=FunAudioLLM/CosyVoice2-0.5B:anna

# ASR配置
ASR_API_KEY=sk-your-asr-api-key-here
ASR_API_URL=https://api.siliconflow.cn/v1/audio/transcriptions
ASR_MODEL=FunAudioLLM/SenseVoiceSmall

# Chat配置
CHAT_API_KEY=sk-your-chat-api-key-here
CHAT_API_URL=https://api.siliconflow.cn/v1
CHAT_MODEL=deepseek-ai/DeepSeek-V3
```

### TTS使用示例

```python
from tts import StreamingTTS

# 创建TTS实例
tts = StreamingTTS.from_env()

try:
    # 文本转语音
    text = "你好，欢迎使用ChatEcho！"
    request_id = tts.send_tts_request(text)
    tts.wait_for_completion()
    print("播放完成")
finally:
    tts.close()
```

### ASR使用示例

```python
from asr import StreamingASR

# 创建ASR实例
asr = StreamingASR.from_env()

try:
    # 音频文件转录
    audio_file = "path/to/your/audio.wav"
    result = asr.transcribe_file(audio_file)
    print(f"转录结果: {result}")
finally:
    asr.close()
```

### Chat使用示例

```python
from chat import ChatBot

# 创建ChatBot实例（自动加载环境配置）
chatbot = ChatBot()

# 简单对话
response = chatbot.chat("你好，请介绍一下自己")
print(f"AI回复: {response}")

# 函数调用示例
response = chatbot.function_call_playground("strawberry中有多少个r？")
print(f"函数调用结果: {response}")
```

### 完整语音处理流程

```python
from tts import StreamingTTS
from asr import StreamingASR
from chat import ChatBot

# 创建实例（自动加载环境配置）
tts = StreamingTTS.from_env()
asr = StreamingASR.from_env()
chatbot = ChatBot()

try:
    # 1. 语音转文本
    audio_file = "input.wav"
    text = asr.transcribe_file(audio_file)
    print(f"识别结果: {text}")
    
    # 2. AI智能回复
    ai_response = chatbot.chat(text)
    print(f"AI回复: {ai_response}")
    
    # 3. 文本转语音
    tts.send_tts_request(ai_response)
    tts.wait_for_completion()
    
finally:
    tts.close()
    asr.close()
```

## 📋 主要依赖

- `pyaudio` - 音频处理
- `requests` - HTTP请求
- `numpy` - 数值计算
- `pydub` - 音频格式处理
- `python-dotenv` - 环境变量管理

## 🔒 注意事项

- 不要将API密钥硬编码在代码中
- 使用 `.env` 文件管理敏感配置
- 确保音频设备正确配置
- 支持的音频格式：WAV、MP3、FLAC等

## 📚 更多信息

- 查看 `tts/README.md` 获取TTS模块详细文档
- 参考 `.env.example` 文件配置环境变量
- 使用 `from_env()` 方法安全加载配置

---

**ChatEcho** - 简单高效的语音处理系统 🎵