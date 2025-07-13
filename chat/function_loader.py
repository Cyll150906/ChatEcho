"""动态函数加载和工具模式生成模块。

实现FunctionLoader类，负责从Python文件动态加载函数、生成OpenAI工具模式和管理函数配置。
"""

import importlib.util
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .exceptions import FunctionLoadError


class FunctionLoader:
    """动态函数加载器。"""
    
    def __init__(self, functions_dir: str = "functions", config_file: str = "functions_config.json"):
        """初始化函数加载器。
        
        Args:
            functions_dir: 函数文件目录
            config_file: 函数配置文件路径
        """
        self.functions_dir = Path(functions_dir)
        self.config_file = Path(config_file)
        self.functions: Dict[str, Callable] = {}
        self.tools: List[Dict[str, Any]] = []
        self.function_configs: Dict[str, Dict[str, Any]] = {}
        
    def load_function_configs(self) -> None:
        """加载函数配置文件。
        
        Raises:
            FunctionLoadError: 配置文件加载失败
        """
        if not self.config_file.exists():
            self.function_configs = {}
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.function_configs = json.load(f)
        except json.JSONDecodeError as e:
            raise FunctionLoadError(f"函数配置文件格式错误: {e}")
        except Exception as e:
            raise FunctionLoadError(f"加载函数配置文件失败: {e}")
    
    def load_functions_from_file(self, file_path: Path) -> Dict[str, Callable]:
        """从Python文件加载函数。
        
        Args:
            file_path: Python文件路径
            
        Returns:
            函数字典
            
        Raises:
            FunctionLoadError: 函数加载失败
        """
        try:
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                raise FunctionLoadError(f"无法加载模块: {file_path}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            functions = {}
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # 只加载在该模块中定义的函数
                if obj.__module__ == module.__name__:
                    functions[name] = obj
                    
            return functions
            
        except Exception as e:
            raise FunctionLoadError(f"加载函数文件失败 {file_path}: {e}")
    
    def generate_tool_schema(self, func: Callable, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """为函数生成OpenAI工具模式。
        
        Args:
            func: 函数对象
            config: 函数配置
            
        Returns:
            工具模式字典
        """
        sig = inspect.signature(func)
        func_name = func.__name__
        
        # 从配置或文档字符串获取描述
        description = ""
        if config and 'description' in config:
            description = config['description']
        elif func.__doc__:
            description = func.__doc__.strip().split('\n')[0]
        else:
            description = f"Function {func_name}"
        
        # 生成参数模式
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_config = {}
            if config and 'parameters' in config and param_name in config['parameters']:
                param_config = config['parameters'][param_name]
            
            # 推断参数类型
            param_type = "string"  # 默认类型
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == str:
                    param_type = "string"
            
            properties[param_name] = {
                "type": param_config.get("type", param_type),
                "description": param_config.get("description", f"Parameter {param_name}")
            }
            
            # 检查是否为必需参数
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "function",
            "function": {
                "name": func_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def load_all_functions(self) -> None:
        """加载所有函数文件。
        
        Raises:
            FunctionLoadError: 函数加载失败
        """
        if not self.functions_dir.exists():
            raise FunctionLoadError(f"函数目录不存在: {self.functions_dir}")
        
        # 加载配置
        self.load_function_configs()
        
        # 清空现有函数和工具
        self.functions.clear()
        self.tools.clear()
        
        # 遍历函数目录中的Python文件
        for py_file in self.functions_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                file_functions = self.load_functions_from_file(py_file)
                
                for func_name, func in file_functions.items():
                    # 检查是否有配置
                    func_config = self.function_configs.get(func_name)
                    
                    # 如果配置中明确禁用了该函数，则跳过
                    if func_config and func_config.get('enabled', True) is False:
                        continue
                    
                    # 添加函数
                    self.functions[func_name] = func
                    
                    # 生成工具模式
                    tool_schema = self.generate_tool_schema(func, func_config)
                    self.tools.append(tool_schema)
                    
            except FunctionLoadError:
                # 重新抛出函数加载错误
                raise
            except Exception as e:
                raise FunctionLoadError(f"处理文件 {py_file} 时发生错误: {e}")
    
    def get_function(self, name: str) -> Optional[Callable]:
        """获取指定名称的函数。
        
        Args:
            name: 函数名称
            
        Returns:
            函数对象，如果不存在则返回None
        """
        return self.functions.get(name)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具模式。
        
        Returns:
            工具模式列表
        """
        return self.tools.copy()
    
    def get_function_names(self) -> List[str]:
        """获取所有函数名称。
        
        Returns:
            函数名称列表
        """
        return list(self.functions.keys())
    
    def reload(self) -> None:
        """重新加载所有函数。
        
        Raises:
            FunctionLoadError: 重新加载失败
        """
        self.load_all_functions()
    
    def create_sample_config(self) -> Dict[str, Any]:
        """创建示例配置文件内容。
        
        Returns:
            示例配置字典
        """
        return {
            "add": {
                "description": "计算两个数的和",
                "enabled": True,
                "parameters": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number", 
                        "description": "第二个数字"
                    }
                }
            },
            "multiply": {
                "description": "计算两个数的乘积",
                "enabled": True,
                "parameters": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                }
            }
        }
    
    def save_sample_config(self) -> None:
        """保存示例配置文件。
        
        Raises:
            FunctionLoadError: 保存失败
        """
        try:
            sample_config = self.create_sample_config()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise FunctionLoadError(f"保存示例配置文件失败: {e}")