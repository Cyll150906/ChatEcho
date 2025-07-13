"""OpenAI函数调用聊天模块。

提供完整的聊天系统和函数调用功能，包括配置管理、函数加载和核心聊天功能。

模块列表：
    config: 聊天设置的配置管理
    core: 支持函数调用的核心聊天功能
    function_loader: 动态函数加载和工具模式生成
    exceptions: 错误处理的自定义异常类
    functions: 一对一映射的单个函数模块
    tools: 对应函数的工具定义JSON文件。
"""

from .config import ChatConfig
from .core import ChatBot
from .exceptions import (
    APIError,
    ArgumentParsingError,
    ChatError,
    ConfigError,
    FunctionLoadError,
)
from .function_loader import FunctionLoader

__version__ = "1.0.0"

__all__ = [
    "APIError",
    "ArgumentParsingError",
    "ChatBot",
    "ChatConfig",
    "ChatError",
    "ConfigError",
    "FunctionLoadError",
    "FunctionLoader",
]