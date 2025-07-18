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
        
        # 添加对话历史管理
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history_length = 20  # 最大保留的对话轮数
    
    def chat(self, prompt: str, model: str = None) -> str:
        """进行聊天对话，支持函数调用和对话历史"""
        if model is None:
            model = self.config.default_model
        
        # 添加用户消息到对话历史
        self.conversation_history.append({'role': 'user', 'content': prompt})
        
        # 管理对话历史长度
        self._manage_history_length()
        
        # 使用完整的对话历史
        messages = self.conversation_history.copy()
        
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
            
            # 将函数调用相关消息添加到对话历史
            self.conversation_history.append(response.choices[0].message)
            self.conversation_history.append({
                'role': 'tool',
                'content': f'{func_result}',
                'tool_call_id': tool_call.id
            })
            
            # 更新messages为最新的对话历史
            messages = self.conversation_history.copy()
            print(messages)
            
            # 第二次调用LLM获取最终回答，使用不同的模型
            final_response = self.llm_client.chat_completion(
                messages=messages,
                model="Qwen/Qwen2.5-7B-Instruct",
                tools=self.tools
            )
            
            # 将最终回答添加到对话历史
            final_content = final_response.choices[0].message.content
            self.conversation_history.append({'role': 'assistant', 'content': final_content})
            return final_content
        
        # 检查是否有自定义格式的工具调用
        elif response_content and '<｜tool▁call▁begin｜>' in response_content:
            result = self._handle_custom_tool_call(response_content, messages, model)
            # 将最终回答添加到对话历史
            self.conversation_history.append({'role': 'assistant', 'content': result})
            return result
        
        else:
            # 普通对话，将助手回复添加到对话历史
            self.conversation_history.append({'role': 'assistant', 'content': response_content})
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
        import json
        func1_args_dict = json.loads(func1_args)
        func1_out = self.function_caller.call_function(func1_name, func1_args_dict)
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
    
    def _manage_history_length(self):
        """管理对话历史长度，避免上下文过长"""
        if len(self.conversation_history) > self.max_history_length:
            # 简单策略：删除最早的消息，但保持偶数个消息（保持对话完整性）
            while len(self.conversation_history) > self.max_history_length:
                # 删除最早的消息
                if self.conversation_history:
                    self.conversation_history.pop(0)
                else:
                    break
    
    def _get_message_role(self, msg):
        """获取消息的角色，兼容不同类型的消息对象"""
        if isinstance(msg, dict):
            return msg.get('role')
        elif hasattr(msg, 'role'):
            return msg.role
        else:
            return None
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self.logger.info("对话历史已清空")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取当前对话历史"""
        return self.conversation_history.copy()
    
    def set_max_history_length(self, length: int):
        """设置最大对话历史长度"""
        if length < 2:
            raise ValueError("最大历史长度不能小于2")
        self.max_history_length = length
        self._manage_history_length()
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        if not self.conversation_history:
            return "暂无对话历史"
        
        user_count = 0
        assistant_count = 0
        tool_count = 0
        
        for msg in self.conversation_history:
            role = self._get_message_role(msg)
            if role == 'user':
                user_count += 1
            elif role == 'assistant':
                assistant_count += 1
            elif role == 'tool':
                tool_count += 1
        
        return f"总消息数: {len(self.conversation_history)}, 用户消息: {user_count}, 助手回复: {assistant_count}, 工具调用: {tool_count}"