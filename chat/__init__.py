# Chat module for function calling with LLM

# 核心类
from .core import ChatBot
from .llm_client import LLMClient
from .function_caller import FunctionCaller

# 配置类
from .config import ChatConfig

# 异常类
from .exceptions import (
    ChatError,
    LLMError,
    FunctionCallError,
    ConfigurationError
)

# 日志配置
from .logging_config import setup_logging

# 导入环境配置（自动加载.env文件）
from .env_config import load_from_env, validate_api_key, get_secure_config, format_api_key

__version__ = "1.0.0"

__all__ = [
    # 核心类
    'ChatBot',
    'LLMClient',
    'FunctionCaller',
    
    # 配置类
    'ChatConfig',
    
    # 异常类
    'ChatError',
    'LLMError',
    'FunctionCallError',
    'ConfigurationError',
    
    # 工具函数
    'setup_logging',
    'load_from_env',
    'validate_api_key',
    'get_secure_config',
    'format_api_key'
]