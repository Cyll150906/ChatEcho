# TTS 流式语音合成包

一个功能完整的流式文本转语音(TTS)Python包，支持实时音频播放、多线程处理和灵活的配置管理。

## 功能特性

- 🎵 **流式音频播放**: 支持实时流式音频播放，无需等待完整音频生成
- 🔧 **模块化设计**: 清晰的模块分离，易于维护和扩展
- ⚙️ **灵活配置**: 支持自定义音频参数和API配置
- 🎛️ **播放控制**: 支持暂停、恢复、停止等播放控制功能
- 🛡️ **异常处理**: 完善的异常处理机制
- 🔨 **实用工具**: 丰富的音频处理和文件操作工具函数

## 包结构

```
tts/
├── __init__.py          # 包初始化，导出所有公共接口
├── core.py              # 核心StreamingTTS类
├── player.py            # 音频播放器模块
├── request_handler.py   # TTS请求处理模块
├── audio_utils.py       # 音频处理工具
├── config.py            # 配置管理模块
├── exceptions.py        # 自定义异常类
├── utils.py             # 通用工具函数
├── examples.py          # 使用示例
└── README.md            # 说明文档
```

## 快速开始

### 基础使用

```python
from tts import StreamingTTS

# 创建TTS实例
tts = StreamingTTS()

try:
    # 发送TTS请求
    text = "你好，这是一个TTS测试。"
    request_id = tts.send_tts_request(text)
    
    # 等待播放完成
    tts.wait_for_completion()
    
finally:
    # 关闭TTS系统
    tts.close()
```

### 高级配置

```python
from tts import StreamingTTS, AudioConfig, APIConfig, TTSConfig

# 自定义音频配置
audio_config = AudioConfig(
    rate=48000,      # 采样率
    chunk=4096,      # 缓冲区大小
    channels=1       # 声道数
)

# 自定义API配置
api_config = APIConfig(
    url="your_api_url",
    key="your_api_key",
    default_model="your_model",
    default_voice="your_voice"
)

# 创建配置
config = TTSConfig(audio=audio_config, api=api_config)

# 使用配置创建TTS实例
tts = StreamingTTS(
    format=config.audio.format,
    channels=config.audio.channels,
    rate=config.audio.rate,
    chunk=config.audio.chunk
)
```

### 播放控制

```python
from tts import StreamingTTS
import time

tts = StreamingTTS()

try:
    # 开始播放
    request_id = tts.send_tts_request("这是一段较长的测试文本...")
    
    # 播放2秒后暂停
    time.sleep(2)
    tts.pause()
    
    # 暂停2秒后恢复
    time.sleep(2)
    tts.resume()
    
    # 停止当前播放
    tts.stop_current_playback()
    
finally:
    tts.close()
```

## 核心模块

### StreamingTTS (核心类)

主要的TTS接口类，整合了所有功能模块。

**主要方法:**
- `send_tts_request(text, **kwargs)`: 发送TTS请求
- `stop_current_playback()`: 停止当前播放
- `pause()`: 暂停播放
- `resume()`: 恢复播放
- `is_playing()`: 检查播放状态
- `wait_for_completion()`: 等待播放完成
- `close()`: 关闭TTS系统

### AudioPlayer (音频播放器)

负责音频数据的播放和播放控制。

**主要功能:**
- 多线程音频播放
- 播放队列管理
- 播放状态控制

### TTSRequestHandler (请求处理器)

处理TTS API请求和流式响应。

**主要功能:**
- API请求发送
- 流式响应处理
- 音频数据解析

## 配置系统

### AudioConfig (音频配置)

```python
from tts import AudioConfig, AudioFormats, SampleRates, Channels

config = AudioConfig(
    format=AudioFormats.INT16,    # 音频格式
    channels=Channels.MONO,       # 声道数
    rate=SampleRates.RATE_44K,    # 采样率
    chunk=2048                    # 缓冲区大小
)
```

### APIConfig (API配置)

```python
from tts import APIConfig

config = APIConfig(
    url="https://api.example.com/tts",
    key="your_api_key",
    default_model="model_name",
    default_voice="voice_name"
)
```

## 异常处理

包提供了完整的异常处理体系：

```python
from tts import (
    TTSError,           # 基础异常
    AudioError,         # 音频异常
    RequestError,       # 请求异常
    APIError,           # API异常
    NetworkError,       # 网络异常
    ConfigError         # 配置异常
)

try:
    tts = StreamingTTS()
    tts.send_tts_request("测试文本")
except APIError as e:
    print(f"API错误: {e}")
except NetworkError as e:
    print(f"网络错误: {e}")
except TTSError as e:
    print(f"TTS错误: {e}")
```

## 工具函数

### 音频处理工具

```python
from tts import (
    save_audio_to_file,
    load_audio_from_file,
    calculate_audio_duration,
    convert_audio_format
)

# 保存音频
save_audio_to_file(audio_data, "output.wav")

# 加载音频
audio_data, channels, sample_width, frame_rate = load_audio_from_file("input.wav")

# 计算时长
duration = calculate_audio_duration(audio_data)
```

### 实用工具

```python
from tts import (
    generate_request_id,
    format_duration,
    validate_audio_config
)

# 生成请求ID
req_id = generate_request_id("prefix")

# 格式化时长
formatted = format_duration(125.5)  # "2分5.5秒"

# 验证配置
is_valid = validate_audio_config(format, channels, rate, chunk)
```

## 依赖要求

- Python 3.7+
- pyaudio
- requests
- numpy
- pydub (可选，用于高级音频处理)

## 安装依赖

```bash
pip install pyaudio requests numpy pydub
```

## 使用示例

查看 `examples.py` 文件获取更多详细的使用示例，包括：

- 基础使用示例
- 高级配置示例
- 播放控制示例
- 错误处理示例
- 工具函数示例

## 注意事项

1. **API密钥安全**: 请妥善保管您的API密钥，不要在代码中硬编码
2. **资源管理**: 使用完毕后请调用 `close()` 方法释放音频资源
3. **网络连接**: 确保网络连接稳定，以获得最佳的流式播放体验
4. **音频设备**: 确保系统音频设备正常工作

## 版本信息

当前版本: 1.0.0

## 许可证

本项目采用 MIT 许可证。