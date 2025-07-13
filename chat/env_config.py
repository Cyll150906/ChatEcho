"""Chat环境变量配置模块

处理环境变量加载和配置验证，确保Chat系统能够正确获取配置信息。
"""

import os
from pathlib import Path
from typing import Optional
from .config import ChatConfig
from .exceptions import ConfigurationError

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    
    # 查找项目根目录的.env文件
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # 回到ChatEcho目录
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file, override=True)  # 强制覆盖已存在的环境变量
        print(f"✅ 自动加载环境配置文件: {env_file}")
except ImportError:
    # python-dotenv未安装时的优雅降级
    pass


def load_from_env() -> ChatConfig:
    """从环境变量加载配置"""
    # 获取原始API密钥
    raw_api_key = (
        os.getenv('CHAT_API_KEY') or 
        os.getenv('OPENAI_API_KEY') or 
        os.getenv('SILICONFLOW_API_KEY') or
        ''
    )
    
    # 格式化API密钥
    formatted_api_key = format_api_key(raw_api_key)
    
    # 获取基础URL
    base_url = (
        os.getenv('CHAT_BASE_URL') or 
        os.getenv('OPENAI_BASE_URL') or
        'https://api.siliconflow.cn/v1'
    )
    
    return ChatConfig(
        api_key=formatted_api_key,
        base_url=base_url
    )


def validate_api_key(api_key: str) -> bool:
    """验证API密钥格式
    
    Args:
        api_key: API密钥
        
    Returns:
        是否有效
    """
    if not api_key:
        return False
    
    # 移除Bearer前缀进行验证
    key = api_key.replace('Bearer ', '') if api_key.startswith('Bearer ') else api_key
    
    # 基本格式验证
    return len(key) > 10 and (key.startswith('sk-') or key.replace('-', '').replace('_', '').isalnum())


def format_api_key(api_key: str) -> str:
    """格式化API密钥
    
    Args:
        api_key: 原始API密钥
        
    Returns:
        格式化后的API密钥
    """
    if not api_key:
        return ''
    
    # Chat模块不需要Bearer前缀，直接返回原始密钥
    return api_key


def get_secure_config() -> ChatConfig:
    """获取安全的配置（从环境变量加载并验证）"""
    config = load_from_env()
    
    if not validate_api_key(config.api_key):
        raise ConfigurationError(
            "无效的API密钥。请设置环境变量 CHAT_API_KEY、OPENAI_API_KEY 或 SILICONFLOW_API_KEY，或创建 .env 文件。\n"
            "格式：sk-your-actual-api-key-here\n"
            "参考 .env.example 文件进行配置。"
        )
    
    return config


def get_secure_config_info() -> dict:
    """获取安全的配置信息（隐藏敏感信息）
    
    Returns:
        安全的配置字典
    """
    try:
        config = load_from_env()
        
        # 创建安全副本
        secure_config = {
            'api_key': '',
            'base_url': config.base_url,
            'default_model': config.default_model,
            'default_temperature': config.default_temperature,
            'default_top_p': config.default_top_p
        }
        
        # 隐藏敏感信息
        if config.api_key:
            key = config.api_key
            if len(key) > 8:
                secure_config['api_key'] = f"{key[:4]}...{key[-4:]}"
            else:
                secure_config['api_key'] = "****"
        
        return secure_config
        
    except Exception:
        return {
            'api_key': '未配置',
            'base_url': '未配置',
            'default_model': '未配置',
            'default_temperature': 0.01,
            'default_top_p': 0.95
        }