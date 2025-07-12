# ChatEcho - 完整语音处理系统

一个基于Python的高性能语音处理系统，集成了文本转语音(TTS)和自动语音识别(ASR)功能，支持实时音频播放、语音转录、多线程处理和模块化架构设计。

## 🚀 项目特性

### TTS (文本转语音) 功能
- **🎵 流式音频播放**: 支持实时流式音频播放，无需等待完整音频生成
- **🎛️ 播放控制**: 支持暂停、恢复、停止等完整播放控制功能
- **⚙️ 灵活配置**: 支持自定义音频参数和API配置

### ASR (自动语音识别) 功能
- **🎤 实时语音识别**: 支持流式音频输入和实时转录
- **📁 文件转录**: 支持多种音频格式的文件转录
- **🔊 设备检测**: 自动检测和配置音频输入设备
- **📝 多格式支持**: 支持WAV、MP3、FLAC等多种音频格式

### 通用特性
- **🏗️ 模块化架构**: 清晰的模块分离，易于维护和扩展
- **🛡️ 异常处理**: 完善的异常处理机制和错误恢复
- **🔧 丰富工具**: 提供音频处理、文件操作等实用工具函数
- **📚 完整文档**: 详细的API文档和使用示例
- **🔒 安全配置**: 支持环境变量配置，保护API密钥安全

## 📁 项目结构

```
ChatEcho/
├── tts/                    # TTS核心包
│   ├── __init__.py         # 包初始化和公共接口
│   ├── core.py             # 核心StreamingTTS类
│   ├── player.py           # 音频播放器模块
│   ├── request_handler.py  # TTS请求处理模块
│   ├── audio_utils.py      # 音频处理工具
│   ├── config.py           # 配置管理模块
│   ├── exceptions.py       # 自定义异常类
│   ├── utils.py            # 通用工具函数
│   └── README.md           # TTS包详细文档
├── asr/                    # ASR核心包
│   ├── __init__.py         # 包初始化和公共接口
│   ├── core.py             # 核心StreamingASR类
│   ├── transcriber.py      # 语音转录模块
│   ├── config.py           # ASR配置管理
│   ├── exceptions.py       # ASR异常类
│   └── utils.py            # ASR工具函数
├── env_config.py           # 环境配置管理
├── .env.example            # 环境变量示例文件
├── .gitignore              # Git忽略文件
├── README.md               # 项目说明文档
├── requirements.txt        # 项目依赖
├── pyproject.toml          # 项目配置文件
└── UPLOAD_TO_GITHUB.md     # GitHub上传指南
```

## 🛠️ 安装要求

### 系统要求
- Python 3.7+
- Windows/Linux/macOS
- 音频输出设备

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- `pyaudio` - 音频播放和录制
- `requests` - HTTP请求处理
- `numpy` - 数值计算
- `pydub` - 音频格式处理
- `python-dotenv` - 环境变量管理

## 🚀 快速开始

### 🔒 环境配置（推荐）

1. **复制环境配置文件**:
   ```bash
   cp .env.example .env
   ```

2. **编辑.env文件，设置您的API密钥**:
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
   
   # 音频配置
   AUDIO_SAMPLE_RATE=16000
   AUDIO_CHANNELS=1
   AUDIO_CHUNK_SIZE=1024
   ```
   注意：只需要填入 sk- 开头的密钥，Bearer 前缀会自动添加

### 🎵 TTS使用示例

```python
from tts import StreamingTTS

# 从环境变量创建TTS实例
tts = StreamingTTS.from_env()

try:
    # 发送TTS请求
    text = "你好，欢迎使用ChatEcho TTS系统！"
    request_id = tts.send_tts_request(text)
    print(f"开始播放: {request_id}")
    
    # 等待播放完成
    tts.wait_for_completion()
    print("播放完成")
    
finally:
    # 关闭TTS系统
    tts.close()
```

### 🎤 ASR使用示例

```python
from asr import StreamingASR

# 从环境变量创建ASR实例
asr = StreamingASR.from_env()

try:
    # 文件转录
    audio_file = "path/to/your/audio.wav"
    result = asr.transcribe_file(audio_file)
    print(f"转录结果: {result}")
    
    # 检测音频设备
    devices = asr.list_audio_devices()
    print(f"可用音频设备: {len(devices)}个")
    
finally:
    # 关闭ASR系统
    asr.close()
```

### 🔄 完整语音处理流程

```python
from tts import StreamingTTS
from asr import StreamingASR

# 创建TTS和ASR实例
tts = StreamingTTS.from_env()
asr = StreamingASR.from_env()

try:
    # 1. 语音识别：将音频文件转为文本
    audio_file = "input.wav"
    recognized_text = asr.transcribe_file(audio_file)
    print(f"识别结果: {recognized_text}")
    
    # 2. 文本处理（可选）
    processed_text = f"您刚才说的是：{recognized_text}"
    
    # 3. 文本转语音：将处理后的文本转为语音播放
    request_id = tts.send_tts_request(processed_text)
    print(f"开始播放回复: {request_id}")
    
    # 等待播放完成
    tts.wait_for_completion()
    print("语音处理流程完成")
    
finally:
    # 关闭系统
    tts.close()
    asr.close()
```

### 🔧 高级配置

#### TTS高级配置

```python
from tts import StreamingTTS, AudioConfig, APIConfig

# 自定义音频配置
audio_config = AudioConfig(
    rate=48000,      # 48kHz采样率
    chunk=4096,      # 4KB缓冲区
    channels=1       # 单声道
)

# 自定义API配置
api_config = APIConfig(
    url="your_api_url",
    key="your_api_key",
    default_model="your_model",
    default_voice="your_voice"
)

# 创建TTS实例
tts = StreamingTTS.create_with_config(audio_config, api_config)
```

#### ASR高级配置

```python
from asr import StreamingASR, AudioConfig, APIConfig

# 自定义音频配置
audio_config = AudioConfig(
    sample_rate=16000,
    channels=1,
    chunk_size=1024
)

# 自定义API配置
api_config = APIConfig(
    url="your_asr_api_url",
    key="your_api_key",
    model="your_asr_model"
)

# 创建ASR实例
asr = StreamingASR.create_with_config(audio_config, api_config)
```

### 播放控制

```python
import time
from tts import StreamingTTS

tts = StreamingTTS()

try:
    # 开始播放长文本
    long_text = "这是一段很长的测试文本..." * 10
    tts.send_tts_request(long_text)
    
    # 播放控制演示
    time.sleep(2)
    tts.pause()          # 暂停播放
    
    time.sleep(2)
    tts.resume()         # 恢复播放
    
    time.sleep(2)
    tts.stop_current_playback()  # 停止播放
    
finally:
    tts.close()
```

## 📖 详细文档

### API文档
- 查看 `tts/README.md` 获取TTS模块的完整API文档
- 查看 `asr/` 目录了解ASR模块的详细实现

### 功能特性

#### TTS功能
- 流式音频播放和缓冲管理
- 播放控制（暂停、恢复、停止）
- 多种音频格式支持
- API请求重试和错误恢复

#### ASR功能
- 音频文件转录（支持WAV、MP3、FLAC等格式）
- 音频设备检测和配置
- 实时语音识别（开发中）
- 音频预处理和格式转换

## 🏗️ 架构设计

### TTS核心组件

1. **StreamingTTS (TTS核心类)**
   - 统一的TTS接口
   - 组件协调和管理
   - 向后兼容性保证

2. **AudioPlayer (音频播放器)**
   - 多线程音频播放
   - 播放队列管理
   - 播放状态控制

3. **TTSRequestHandler (TTS请求处理器)**
   - API请求管理
   - 流式响应处理
   - 音频数据解析

### ASR核心组件

1. **StreamingASR (ASR核心类)**
   - 统一的ASR接口
   - 音频输入管理
   - 转录结果处理

2. **SpeechTranscriber (语音转录器)**
   - 文件转录处理
   - API请求管理
   - 重试机制

3. **音频设备管理**
   - 设备检测和枚举
   - 音频参数配置
   - 设备状态监控

### 通用组件

1. **配置系统**
   - 环境变量管理
   - 配置验证和加载
   - 预定义常量

2. **异常处理**
   - 分层异常体系
   - 详细错误信息
   - 优雅错误恢复

### 设计原则

- **单一职责**: 每个模块专注于特定功能
- **开放封闭**: 易于扩展，稳定的接口
- **依赖倒置**: 面向接口编程
- **配置分离**: 配置与代码分离

## 🔧 配置说明

### 环境变量配置

项目支持通过环境变量进行配置，推荐使用 `.env` 文件：

```bash
# TTS配置
TTS_API_KEY=sk-your-tts-api-key
TTS_API_URL=https://api.siliconflow.cn/v1/audio/speech
TTS_MODEL=FunAudioLLM/CosyVoice2-0.5B
TTS_VOICE=FunAudioLLM/CosyVoice2-0.5B:anna

# ASR配置
ASR_API_KEY=sk-your-asr-api-key
ASR_API_URL=https://api.siliconflow.cn/v1/audio/transcriptions
ASR_MODEL=FunAudioLLM/SenseVoiceSmall

# 音频配置
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=1024
```

### TTS音频配置

```python
from tts import AudioConfig, AudioFormats, SampleRates

config = AudioConfig(
    format=AudioFormats.INT16,     # 16位整数格式
    channels=1,                    # 单声道
    rate=SampleRates.RATE_44K,     # 44.1kHz采样率
    chunk=2048                     # 2KB缓冲区
)
```

### ASR音频配置

```python
from asr import AudioConfig

config = AudioConfig(
    sample_rate=16000,             # 16kHz采样率
    channels=1,                    # 单声道
    chunk_size=1024                # 1KB缓冲区
)
```

## 🛡️ 异常处理

系统提供完整的异常处理体系：

### TTS异常处理

```python
from tts import (
    TTSError,           # 基础TTS异常
    AudioError,         # 音频相关异常
    RequestError,       # 请求相关异常
    APIError,           # API异常
    NetworkError,       # 网络异常
    ConfigError         # 配置异常
)

try:
    tts = StreamingTTS.from_env()
    tts.send_tts_request("测试文本")
except APIError as e:
    print(f"TTS API错误: {e}")
except NetworkError as e:
    print(f"网络错误: {e}")
except TTSError as e:
    print(f"TTS系统错误: {e}")
```

### ASR异常处理

```python
from asr import (
    ASRError,           # 基础ASR异常
    TranscriptionError, # 转录异常
    AudioDeviceError,   # 音频设备异常
    ConfigError         # 配置异常
)

try:
    asr = StreamingASR.from_env()
    result = asr.transcribe_file("audio.wav")
except TranscriptionError as e:
    print(f"转录错误: {e}")
except AudioDeviceError as e:
    print(f"音频设备错误: {e}")
except ASRError as e:
    print(f"ASR系统错误: {e}")
```

## 🔨 开发指南

### 扩展新功能

1. **添加新的音频格式支持**
   - 在 `audio_utils.py` 中添加解析函数
   - 在 `config.py` 中添加格式常量

2. **支持新的TTS API**
   - 继承 `TTSRequestHandler` 类
   - 实现特定的请求处理逻辑

3. **添加音频效果**
   - 在 `AudioPlayer` 中添加音频处理管道
   - 使用 `utils.py` 中的音频处理函数

### 测试

```bash
# 运行基础测试
python example/tts_example.py

# 测试特定功能
python -c "from tts import StreamingTTS; tts = StreamingTTS(); print('TTS初始化成功')"
```

## 📝 更新日志

### v1.0.0 (2024-12-XX)
- ✨ 初始版本发布
- 🏗️ 完整的模块化架构
- 🎵 TTS流式音频播放支持
- 🎤 ASR语音识别功能
- ⚙️ 灵活的配置系统
- 🔒 环境变量安全配置
- 🛡️ 完善的异常处理
- 📚 详细的文档和示例
- 🔧 音频设备检测和管理
- 📁 多格式音频文件支持

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyAudio](https://pypi.org/project/PyAudio/) - 音频I/O库
- [Requests](https://requests.readthedocs.io/) - HTTP库
- [NumPy](https://numpy.org/) - 数值计算库
- [SiliconFlow](https://siliconflow.cn/) - TTS API服务

## 📋 注意事项

### 🔒 安全性
- **重要**: 不要将API密钥硬编码在代码中
- 使用环境变量或.env文件管理敏感配置
- 将.env文件添加到.gitignore中
- 定期轮换API密钥

### 🛠️ 技术要求

#### 通用要求
- 确保已正确安装PyAudio依赖
- API密钥需要有效的SiliconFlow账户
- 网络连接稳定性影响API调用效果
- 建议在生产环境中添加适当的错误处理和重试机制

#### TTS特定要求
- 音频播放可能因系统音频设备配置而异
- 流式播放需要稳定的网络连接
- 建议使用高质量的音频输出设备

#### ASR特定要求
- 音频输入设备需要正确配置和权限
- 支持的音频格式：WAV、MP3、FLAC等
- 音频文件质量影响识别准确率
- 建议使用16kHz采样率的单声道音频

### 📈 性能优化

#### TTS性能优化
- 对于高频使用场景，建议实现音频缓存
- 考虑使用连接池减少网络开销
- 监控API调用频率，避免触发限流
- 合理设置音频缓冲区大小

#### ASR性能优化
- 预处理音频文件以提高识别准确率
- 批量处理多个音频文件时考虑并发控制
- 对于大文件，考虑分段处理
- 缓存常用的音频设备配置

### 📚 更多信息
- 查看 `tts/README.md` 获取TTS模块的详细文档
- 查看 `UPLOAD_TO_GITHUB.md` 了解如何上传项目到GitHub
- 参考 `.env.example` 文件配置环境变量
- 使用 `from_env()` 方法从环境变量安全加载配置

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/ChatEcho/issues)
- 发送邮件至: your.email@example.com

---

**ChatEcho** - 让文本转语音更简单、更高效！ 🎵