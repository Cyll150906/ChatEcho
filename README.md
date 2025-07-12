# ChatEcho - 流式TTS语音合成系统

一个基于Python的高性能流式文本转语音(TTS)系统，支持实时音频播放、多线程处理和模块化架构设计。

## 🚀 项目特性

- **🎵 流式音频播放**: 支持实时流式音频播放，无需等待完整音频生成
- **🏗️ 模块化架构**: 清晰的模块分离，易于维护和扩展
- **⚙️ 灵活配置**: 支持自定义音频参数和API配置
- **🎛️ 播放控制**: 支持暂停、恢复、停止等完整播放控制功能
- **🛡️ 异常处理**: 完善的异常处理机制和错误恢复
- **🔧 丰富工具**: 提供音频处理、文件操作等实用工具函数
- **📚 完整文档**: 详细的API文档和使用示例

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
├── example/                # 示例代码
│   └── tts_example.py      # TTS使用示例
├── README.md               # 项目说明文档
└── requirements.txt        # 项目依赖
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
- `pydub` - 音频格式处理（可选）

## 🚀 快速开始

### 🔒 安全配置（推荐）

1. **复制环境配置文件**:
   ```bash
   cp .env.example .env
   ```

2. **编辑.env文件，设置您的API密钥**:
   ```bash
   TTS_API_KEY=sk-your-actual-api-key-here
   ```
   注意：只需要填入 sk- 开头的密钥，Bearer 前缀会自动添加

3. **使用安全配置**:
   ```python
   from tts import StreamingTTS, get_secure_config
   
   # 从环境变量加载安全配置（自动格式化API密钥）
   config = get_secure_config()
   tts = StreamingTTS(config=config)
   
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

### 基础使用（不推荐用于生产环境）

```python
from tts import StreamingTTS

# 创建TTS实例
tts = StreamingTTS()

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

### 高级配置

```python
from tts import StreamingTTS, AudioConfig, APIConfig

# 自定义音频配置
audio_config = AudioConfig(
    rate=48000,      # 48kHz采样率
    chunk=4096,      # 4KB缓冲区
    channels=1       # 单声道
)

# 创建TTS实例
tts = StreamingTTS(
    format=audio_config.format,
    channels=audio_config.channels,
    rate=audio_config.rate,
    chunk=audio_config.chunk
)

# 自定义API配置
tts.set_api_config(
    api_url="your_api_url",
    api_key="your_api_key",
    default_model="your_model",
    default_voice="your_voice"
)
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
查看 `tts/README.md` 获取完整的API文档和模块说明。

### 使用示例
运行示例代码：
```bash
python example/tts_example.py
```

示例包含：
- 基础使用演示
- 高级配置示例
- 播放控制功能
- 错误处理机制
- 工具函数使用

## 🏗️ 架构设计

### 核心组件

1. **StreamingTTS (核心类)**
   - 统一的TTS接口
   - 组件协调和管理
   - 向后兼容性保证

2. **AudioPlayer (音频播放器)**
   - 多线程音频播放
   - 播放队列管理
   - 播放状态控制

3. **TTSRequestHandler (请求处理器)**
   - API请求管理
   - 流式响应处理
   - 音频数据解析

4. **配置系统**
   - 灵活的配置管理
   - 预定义常量
   - 配置验证

5. **异常处理**
   - 分层异常体系
   - 详细错误信息
   - 优雅错误恢复

### 设计原则

- **单一职责**: 每个模块专注于特定功能
- **开放封闭**: 易于扩展，稳定的接口
- **依赖倒置**: 面向接口编程
- **配置分离**: 配置与代码分离

## 🔧 配置说明

### 音频配置

```python
from tts import AudioConfig, AudioFormats, SampleRates

config = AudioConfig(
    format=AudioFormats.INT16,     # 16位整数格式
    channels=1,                    # 单声道
    rate=SampleRates.RATE_44K,     # 44.1kHz采样率
    chunk=2048                     # 2KB缓冲区
)
```

### API配置

```python
from tts import APIConfig

api_config = APIConfig(
    url="https://api.siliconflow.cn/v1/audio/speech",
    key="your_api_key",
    default_model="FunAudioLLM/CosyVoice2-0.5B",
    default_voice="FunAudioLLM/CosyVoice2-0.5B:anna"
)
```

## 🛡️ 异常处理

系统提供完整的异常处理体系：

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
    tts = StreamingTTS()
    tts.send_tts_request("测试文本")
except APIError as e:
    print(f"API错误: {e}")
except NetworkError as e:
    print(f"网络错误: {e}")
except TTSError as e:
    print(f"TTS系统错误: {e}")
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
- 🎵 流式音频播放支持
- ⚙️ 灵活的配置系统
- 🛡️ 完善的异常处理
- 📚 详细的文档和示例

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
- 确保已正确安装PyAudio依赖
- API密钥需要有效的SiliconFlow账户
- 网络连接稳定性影响流式播放效果
- 建议在生产环境中添加适当的错误处理和重试机制
- 音频播放可能因系统音频设备配置而异

### 📈 性能优化
- 对于高频使用场景，建议实现音频缓存
- 考虑使用连接池减少网络开销
- 监控API调用频率，避免触发限流

### 📚 更多信息
- 查看 [IMPROVEMENTS.md](IMPROVEMENTS.md) 获取详细的代码质量改进建议
- 参考 [example/secure_tts_example.py](example/secure_tts_example.py) 了解安全使用方法

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/yourusername/ChatEcho/issues)
- 发送邮件至: your.email@example.com

---

**ChatEcho** - 让文本转语音更简单、更高效！ 🎵