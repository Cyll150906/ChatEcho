"""核心聊天功能模块。

实现ChatBot类，提供函数执行、API交互和聊天流程管理功能。
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI

from .config import ChatConfig
from .exceptions import APIError, ArgumentParsingError, ChatError
from .function_loader import FunctionLoader


class ChatBot:
    """支持函数调用的聊天机器人。"""
    
    def __init__(self, config: Optional[ChatConfig] = None, function_loader: Optional[FunctionLoader] = None):
        """初始化聊天机器人。
        
        Args:
            config: 聊天配置，如果为None则从环境变量加载
            function_loader: 函数加载器，如果为None则创建默认加载器
        """
        # 初始化配置
        if config is None:
            self.config = ChatConfig.from_env()
        else:
            self.config = config
        
        # 验证配置
        self.config.validate()
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        
        # 初始化函数加载器
        if function_loader is None:
            self.function_loader = FunctionLoader(
                functions_dir=self.config.functions_dir,
                config_file=self.config.functions_config_file
            )
        else:
            self.function_loader = function_loader
        
        # 加载函数
        try:
            self.function_loader.load_all_functions()
        except Exception as e:
            # 如果函数加载失败，记录错误但不阻止初始化
            print(f"警告: 函数加载失败: {e}")
    
    def _clean_function_arguments(self, args_str: str) -> str:
        """清理函数参数字符串。
        
        Args:
            args_str: 原始参数字符串
            
        Returns:
            清理后的参数字符串
        """
        # 清理参数字符串，移除markdown代码块和特殊字符
        cleaned_args = args_str.strip()
        
        # 移除markdown代码块标记
        cleaned_args = re.sub(r'```[^`]*```', '', cleaned_args)
        
        # 移除特殊的工具调用标记
        cleaned_args = re.sub(r'<｜[^｜]*｜>', '', cleaned_args)
        
        # 移除所有换行符和多余空格
        cleaned_args = re.sub(r'\s+', ' ', cleaned_args)
        cleaned_args = cleaned_args.strip()
        
        # 尝试提取JSON部分
        json_match = re.search(r'\{[^}]+\}', cleaned_args)
        if json_match:
            cleaned_args = json_match.group(0)
        
        return cleaned_args
    
    def _execute_function(self, function_name: str, arguments: str) -> Any:
        """执行函数调用。
        
        Args:
            function_name: 函数名称
            arguments: 函数参数JSON字符串
            
        Returns:
            函数执行结果
            
        Raises:
            ArgumentParsingError: 参数解析错误
            ChatError: 函数执行错误
        """
        # 获取函数
        func = self.function_loader.get_function(function_name)
        if func is None:
            raise ChatError(f"函数不存在: {function_name}")
        
        # 清理和解析参数
        try:
            cleaned_args = self._clean_function_arguments(arguments)
            args_dict = json.loads(cleaned_args)
        except json.JSONDecodeError as e:
            raise ArgumentParsingError(f"参数解析失败: {e}")
        
        # 执行函数
        try:
            result = func(**args_dict)
            return result
        except Exception as e:
            raise ChatError(f"函数执行失败 {function_name}: {e}")
    
    def _create_chat_completion(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """创建聊天完成请求。
        
        Args:
            messages: 消息列表
            tools: 工具列表
            
        Returns:
            API响应
            
        Raises:
            APIError: API调用错误
        """
        try:
            kwargs = {
                'model': self.config.model,
                'messages': messages,
                'temperature': self.config.temperature,
                'top_p': self.config.top_p,
                'stream': self.config.stream
            }
            
            if tools:
                kwargs['tools'] = tools
            
            response = self.client.chat.completions.create(**kwargs)
            return response
            
        except Exception as e:
            raise APIError(f"API调用失败: {e}")
    
    def chat(self, prompt: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """进行聊天对话。
        
        Args:
            prompt: 用户输入
            conversation_history: 对话历史
            
        Returns:
            聊天回复
            
        Raises:
            ChatError: 聊天过程中的错误
        """
        # 构建消息列表
        messages = conversation_history.copy() if conversation_history else []
        messages.append({'role': 'user', 'content': prompt})
        
        # 获取工具列表
        tools = self.function_loader.get_tools()
        
        # 第一次API调用
        response = self._create_chat_completion(messages, tools if tools else None)
        
        # 检查是否有工具调用
        if not response.choices[0].message.tool_calls:
            return response.choices[0].message.content or "No response content"
        
        # 处理工具调用
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = tool_call.function.arguments
        
        # 执行函数
        try:
            function_result = self._execute_function(function_name, function_args)
        except (ArgumentParsingError, ChatError) as e:
            return f"函数调用错误: {e}"
        
        # 添加助手消息和工具结果到对话历史
        messages.append(response.choices[0].message)
        messages.append({
            'role': 'tool',
            'content': str(function_result),
            'tool_call_id': tool_call.id
        })
        
        # 第二次API调用获取最终回复
        final_response = self._create_chat_completion(messages, tools if tools else None)
        
        # 处理最终响应
        content = final_response.choices[0].message.content
        
        if content:
            # 如果内容包含特殊的工具调用格式，则清理它
            if '<｜tool▁calls▁begin｜>' in content:
                return str(function_result)
            else:
                return content
        elif final_response.choices[0].message.tool_calls:
            return f"Tool call: {final_response.choices[0].message.tool_calls[0].function.name}"
        else:
            return "No response content"
    
    def chat_with_history(self, prompt: str, conversation_history: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        """进行聊天对话并返回更新的对话历史。
        
        Args:
            prompt: 用户输入
            conversation_history: 对话历史
            
        Returns:
            (回复内容, 更新的对话历史)
        """
        # 复制对话历史
        updated_history = conversation_history.copy()
        
        # 添加用户消息
        updated_history.append({'role': 'user', 'content': prompt})
        
        # 获取回复
        response = self.chat(prompt, conversation_history)
        
        # 添加助手回复
        updated_history.append({'role': 'assistant', 'content': response})
        
        return response, updated_history
    
    def reload_functions(self) -> None:
        """重新加载函数。
        
        Raises:
            ChatError: 重新加载失败
        """
        try:
            self.function_loader.reload()
        except Exception as e:
            raise ChatError(f"重新加载函数失败: {e}")
    
    def get_available_functions(self) -> List[str]:
        """获取可用函数列表。
        
        Returns:
            函数名称列表
        """
        return self.function_loader.get_function_names()
    
    def get_function_tools(self) -> List[Dict[str, Any]]:
        """获取函数工具定义。
        
        Returns:
            工具定义列表
        """
        return self.function_loader.get_tools()
    
    @classmethod
    def create_with_config_file(cls: type['ChatBot'], config_file: str) -> 'ChatBot':
        """从配置文件创建聊天机器人。
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            ChatBot实例
        """
        config = ChatConfig.from_file(config_file)
        return cls(config)
    
    @classmethod
    def create_default(cls: type['ChatBot']) -> 'ChatBot':
        """创建默认配置的聊天机器人。
        
        Returns:
            ChatBot实例
        """
        return cls()