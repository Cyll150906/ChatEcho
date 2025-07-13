"""Chat module for function calling with OpenAI API."""

from .core import ChatBot
from .config import ChatConfig
from .function_loader import FunctionLoader
from .exceptions import ChatError, FunctionLoadError, ConfigError

__all__ = [
    'ChatBot',
    'ChatConfig', 
    'FunctionLoader',
    'ChatError',
    'FunctionLoadError',
    'ConfigError'
]

__version__ = '1.0.0'