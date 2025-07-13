import os
from typing import Optional

class ChatConfig:
    """聊天模块配置管理"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        # 如果没有传入参数，则自动从环境变量加载
        if api_key is None and base_url is None:
            self._load_from_env()
        else:
            self.api_key = api_key or self._get_api_key()
            self.base_url = base_url or self._get_base_url()
            self.default_model = self._get_default_model()
            self.default_temperature = 0.01
            self.default_top_p = 0.95
    
    def _load_from_env(self):
        """从环境变量自动加载配置"""
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.default_model = self._get_default_model()
        self.default_temperature = 0.01
        self.default_top_p = 0.95
    
    def _get_api_key(self) -> str:
        """获取API密钥，优先从环境变量获取"""
        api_key = os.getenv('CHAT_API_KEY')
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            api_key = os.getenv('SILICONFLOW_API_KEY')
        if not api_key:
            raise ValueError(
                "API密钥未设置。请设置环境变量 CHAT_API_KEY、OPENAI_API_KEY 或 SILICONFLOW_API_KEY，"
                "或在创建ChatBot时传入api_key参数"
            )
        return api_key
    
    def _get_base_url(self) -> str:
        """获取API基础URL"""
        return os.getenv('CHAT_BASE_URL') or os.getenv('OPENAI_BASE_URL', 'https://api.siliconflow.cn/v1')
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        return os.getenv('CHAT_MODEL') or os.getenv('OPENAI_MODEL', 'deepseek-ai/DeepSeek-V3')
    
    @classmethod
    def from_env_file(cls, env_file: str = '.env') -> 'ChatConfig':
        """从.env文件加载配置"""
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        return cls()
    
    @classmethod
    def from_env(cls) -> 'ChatConfig':
        """从环境变量加载配置（参考TTS模块方案）"""
        return cls()  # 使用默认构造函数，会自动从环境变量加载