# 上传到GitHub的步骤

## 1. 在GitHub上创建仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 仓库名称：`ChatEcho`
4. 描述：`完整的TTS和ASR语音处理系统 - 支持文字转语音和语音转文字功能`
5. 选择 "Public" (公开仓库)
6. **不要**勾选 "Add a README file"、"Add .gitignore" 或 "Choose a license"
7. 点击 "Create repository"

## 2. 添加远程仓库并推送代码

在项目目录中运行以下命令（将 `YOUR_USERNAME` 替换为你的GitHub用户名）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/ChatEcho.git

# 设置主分支名称
git branch -M main

# 推送代码到GitHub
git push -u origin main
```

## 3. 验证上传

访问你的GitHub仓库页面，确认所有文件都已成功上传。

## 项目结构

```
ChatEcho/
├── .env.example          # 环境变量配置示例
├── .gitignore            # Git忽略文件配置
├── README.md             # 项目说明文档
├── requirements.txt      # Python依赖包列表
├── pyproject.toml        # 项目配置文件
├── asr/                  # ASR语音转文字模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── core.py           # 核心功能
│   ├── env_config.py     # 环境变量配置
│   ├── exceptions.py     # 异常处理
│   ├── recorder.py       # 音频录制
│   ├── transcriber.py    # 语音转录
│   └── utils.py          # 工具函数
└── tts/                  # TTS文字转语音模块
    ├── README.md
    ├── __init__.py
    ├── audio_utils.py     # 音频工具
    ├── config.py         # 配置管理
    ├── core.py           # 核心功能
    ├── env_config.py     # 环境变量配置
    ├── exceptions.py     # 异常处理
    ├── player.py         # 音频播放
    ├── request_handler.py # 请求处理
    └── utils.py          # 工具函数
```

## 功能特性

### TTS (文字转语音)
- 支持多种语音模型和语言
- 灵活的音频格式输出
- 完善的错误处理机制
- 环境变量配置管理

### ASR (语音转文字)
- 实时录音和音频文件转录
- 自动音频设备检测
- API连接状态监控
- 强大的异常处理系统

### 通用特性
- 模块化设计，易于扩展
- 详细的日志和调试信息
- 完整的配置验证
- 跨平台兼容性