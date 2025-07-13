import json
import os
import importlib
import logging
from typing import List, Dict, Any
from .exceptions import FunctionCallError, ToolLoadError

class FunctionCaller:
    def __init__(self, tools_dir: str = None):
        if tools_dir is None:
            tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        self.tools_dir = tools_dir
        self.logger = logging.getLogger(__name__)
        self.tools = self._load_tools()
    
    def _load_tools(self) -> List[Dict[str, Any]]:
        """从tools目录加载所有函数配置"""
        tools = []
        if not os.path.exists(self.tools_dir):
            self.logger.warning(f"Tools directory not found: {self.tools_dir}")
            return tools
        
        for filename in os.listdir(self.tools_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.tools_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tool_config = json.load(f)
                        # 验证工具配置格式
                        self._validate_tool_config(tool_config, filename)
                        tools.append(tool_config)
                        self.logger.debug(f"Loaded tool: {filename}")
                except (json.JSONDecodeError, KeyError) as e:
                    self.logger.error(f"Failed to load tool config {filename}: {e}")
                    raise ToolLoadError(f"Invalid tool configuration in {filename}: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error loading {filename}: {e}")
                    raise ToolLoadError(f"Failed to load {filename}: {e}")
        
        self.logger.info(f"Loaded {len(tools)} tools from {self.tools_dir}")
        return tools
    
    def _validate_tool_config(self, config: Dict[str, Any], filename: str) -> None:
        """验证工具配置格式"""
        required_keys = ['type', 'function']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required key '{key}' in {filename}")
        
        function_config = config['function']
        required_function_keys = ['name', 'description', 'parameters']
        for key in required_function_keys:
            if key not in function_config:
                raise KeyError(f"Missing required function key '{key}' in {filename}")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用的工具配置"""
        return self.tools
    
    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """调用指定的函数"""
        self.logger.debug(f"Calling function: {function_name} with args: {arguments}")
        
        try:
            # 动态导入函数模块
            module_name = f".function_calling.{function_name}"
            module = importlib.import_module(module_name, package=__package__)
            
            # 获取同名函数
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                try:
                    result = func(**arguments)
                    self.logger.debug(f"Function {function_name} returned: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"Error executing function {function_name}: {e}")
                    raise FunctionCallError(f"Error executing function '{function_name}': {e}")
            else:
                error_msg = f"Function '{function_name}' not found in module '{module_name}'"
                self.logger.error(error_msg)
                raise FunctionCallError(error_msg)
        except ImportError as e:
            error_msg = f"Module for function '{function_name}' not found: {e}"
            self.logger.error(error_msg)
            raise FunctionCallError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error calling function '{function_name}': {e}"
            self.logger.error(error_msg)
            raise FunctionCallError(error_msg)