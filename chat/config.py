"""聊天模块配置管理。

提供ChatConfig数据类用于管理聊天设置，包括从文件或环境变量加载配置和验证功能。
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .exceptions import ConfigError


@dataclass
class ChatConfig:
    """Chat configuration class."""
    
    # OpenAI API配置
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    
    # 模型配置
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.01
    top_p: float = 0.95
    stream: bool = False
    
    # 函数配置
    functions_dir: str = "functions"
    functions_config_file: str = "functions_config.json"
    
    # 其他配置
    max_retries: int = 3
    timeout: int = 30
    
    @classmethod
    def from_file(cls: type['ChatConfig'], config_file: str) -> 'ChatConfig':
        """从配置文件加载配置。
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            ChatConfig实例
            
        Raises:
            ConfigError: 配置文件不存在或格式错误
        """
        if not os.path.exists(config_file):
            raise ConfigError(f"配置文件不存在: {config_file}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式错误: {e}")
        except TypeError as e:
            raise ConfigError(f"配置参数错误: {e}")
    
    @classmethod
    def from_env(cls: type['ChatConfig']) -> 'ChatConfig':
        """从环境变量加载配置。
        
        Returns:
            ChatConfig实例
        """
        return cls(
            api_key=os.getenv('CHAT_API_KEY', ''),
            base_url=os.getenv('CHAT_BASE_URL', 'https://api.openai.com/v1'),
            model=os.getenv('CHAT_MODEL', 'gpt-3.5-turbo'),
            temperature=float(os.getenv('CHAT_TEMPERATURE', '0.01')),
            top_p=float(os.getenv('CHAT_TOP_P', '0.95')),
            stream=os.getenv('CHAT_STREAM', 'false').lower() == 'true',
            functions_dir=os.getenv('CHAT_FUNCTIONS_DIR', 'functions'),
            functions_config_file=os.getenv('CHAT_FUNCTIONS_CONFIG_FILE', 'functions_config.json'),
            max_retries=int(os.getenv('CHAT_MAX_RETRIES', '3')),
            timeout=int(os.getenv('CHAT_TIMEOUT', '30'))
        )
    
    def validate(self) -> None:
        """验证配置的有效性。
        
        Raises:
            ConfigError: 配置无效
        """
        if not self.api_key:
            raise ConfigError("API密钥不能为空")
            
        if not self.base_url:
            raise ConfigError("Base URL不能为空")
            
        if not self.model:
            raise ConfigError("模型名称不能为空")
            
        if not 0 <= self.temperature <= 2:
            raise ConfigError("temperature必须在0-2之间")
            
        if not 0 <= self.top_p <= 1:
            raise ConfigError("top_p必须在0-1之间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。
        
        Returns:
            配置字典
        """
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'model': self.model,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'stream': self.stream,
            'functions_dir': self.functions_dir,
            'functions_config_file': self.functions_config_file,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }
    
    def save_to_file(self, config_file: str) -> None:
        """保存配置到文件。
        
        Args:
            config_file: 配置文件路径
            
        Raises:
            ConfigError: 保存失败
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {e}")