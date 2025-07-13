from openai import OpenAI
from typing import Optional
from .config import ChatConfig

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, config: Optional[ChatConfig] = None):
        if config is None:
            # 使用from_env方法自动加载环境配置
            config = ChatConfig.from_env()
        
        # 参数优先级：传入参数 > 配置对象 > 环境变量
        final_api_key = api_key or config.api_key
        final_base_url = base_url or config.base_url
        
        if not final_api_key or final_api_key == "您的 APIKEY":
            raise ValueError(
                "请设置有效的API密钥。可以通过以下方式之一：\n"
                "1. 设置环境变量 OPENAI_API_KEY 或 SILICONFLOW_API_KEY\n"
                "2. 在创建LLMClient时传入api_key参数\n"
                "3. 使用.env文件配置"
            )
        
        self.client = OpenAI(
            api_key=final_api_key,
            base_url=final_base_url
        )
        self.config = config
    
    def chat_completion(self, messages, model="deepseek-ai/DeepSeek-V2.5", 
                       temperature=0.01, top_p=0.95, stream=False, tools=None):
        """发送聊天完成请求"""
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            tools=tools
        )