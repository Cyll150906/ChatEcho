import json
import logging
from typing import List, Dict, Any, Optional
from .llm_client import LLMClient
from .function_caller import FunctionCaller
from .config import ChatConfig

# 导入函数调用模块中的函数，以便eval()可以使用
from .function_calling.add import add
from .function_calling.mul import mul
from .function_calling.compare import compare
from .function_calling.count_letter_in_string import count_letter_in_string

class ChatBot:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, config: Optional[ChatConfig] = None):
        if config is None:
            # 参考TTS模块方案，优先使用from_env方法自动加载环境配置
            try:
                config = ChatConfig.from_env()
            except ValueError:
                # 如果环境变量加载失败，尝试从.env文件加载
                try:
                    config = ChatConfig.from_env_file()
                except ValueError:
                    config = ChatConfig()
        
        self.config = config
        self.llm_client = LLMClient(api_key, base_url, config)
        self.function_caller = FunctionCaller()
        self.tools = self.function_caller.get_tools()
        self.logger = logging.getLogger(__name__)
    
    def chat(self, prompt: str, model: str = None) -> str:
        """进行聊天对话，支持函数调用"""
        if model is None:
            model = self.config.default_model
            
        messages = [{'role': 'user', 'content': prompt}]
        
        # 第一次调用LLM
        response = self.llm_client.chat_completion(
            messages=messages,
            model=model,
            tools=self.tools
        )
        
        print(response)
        self.logger.debug(f"LLM Response: {response.choices[0].message}")
        
        response_content = response.choices[0].message.content
        
        # 检查是否有标准的工具调用
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments
            
            # 使用eval执行函数调用（参照fuc_call.py的方案）
            func_result = eval(f'{func_name}(**{func_args})')
            print(func_result)
            
            # 将函数调用结果添加到消息历史
            messages.append(response.choices[0].message)
            messages.append({
                'role': 'tool',
                'content': f'{func_result}',
                'tool_call_id': tool_call.id
            })
            print(messages)
            
            # 第二次调用LLM获取最终回答，使用不同的模型
            final_response = self.llm_client.chat_completion(
                messages=messages,
                model="Qwen/Qwen2.5-7B-Instruct",
                tools=self.tools
            )
            return final_response.choices[0].message.content
        
        # 检查是否有自定义格式的工具调用
        elif response_content and '<｜tool▁call▁begin｜>' in response_content:
            return self._handle_custom_tool_call(response_content, messages, model)
        
        else:
            return response_content
    
    def _handle_custom_tool_call(self, response_content: str, messages: list, model: str) -> str:
        """处理自定义格式的工具调用"""
        import re
        
        # 解析工具调用格式: <｜tool▁call▁begin｜>function<｜tool▁sep｜>function_name
        pattern = r'<｜tool▁call▁begin｜>function<｜tool▁sep｜>(\w+)\s*```json\s*({.*?})\s*```<｜tool▁call▁end｜>'
        matches = re.findall(pattern, response_content, re.DOTALL)
        
        if matches:
            func_name, func_args_str = matches[0]
            try:
                func_args = json.loads(func_args_str)
                
                # 执行函数调用
                func_result = self.function_caller.call_function(func_name, func_args)
                
                # 构造新的提示，包含函数执行结果
                result_prompt = f"函数 {func_name} 的执行结果是: {func_result}。请用中文回答用户的问题。"
                messages.append({'role': 'assistant', 'content': response_content})
                messages.append({'role': 'user', 'content': result_prompt})
                
                # 第二次调用LLM获取最终回答
                final_response = self.llm_client.chat_completion(
                    messages=messages,
                    model=model
                )
                return final_response.choices[0].message.content
                
            except (json.JSONDecodeError, Exception) as e:
                self.logger.error(f"Error parsing custom tool call: {e}")
                return f"工具调用解析错误: {e}"
        
        return response_content
    
    def function_call_playground(self, prompt: str) -> str:
        """完全参照fuc_call.py的function_call_playground实现"""
        messages = [{'role': 'user', 'content': prompt}]
        response = self.llm_client.chat_completion(
            model="deepseek-ai/DeepSeek-V2.5",
            messages=messages,
            temperature=0.01,
            top_p=0.95,
            stream=False,
            tools=self.tools
        )
        
        print(response)
        func1_name = response.choices[0].message.tool_calls[0].function.name
        func1_args = response.choices[0].message.tool_calls[0].function.arguments
        func1_out = eval(f'{func1_name}(**{func1_args})')
        print(func1_out)
        
        messages.append(response.choices[0].message)
        messages.append({
            'role': 'tool',
            'content': f'{func1_out}',
            'tool_call_id': response.choices[0].message.tool_calls[0].id
        })
        print(messages)
        response = self.llm_client.chat_completion(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=messages,
            temperature=0.01,
            top_p=0.95,
            stream=False,
            tools=self.tools
        )
        return response.choices[0].message.content