"""Chat模块自定义异常"""

class ChatError(Exception):
    """Chat模块基础异常"""
    pass

class ConfigurationError(ChatError):
    """配置错误"""
    pass

class FunctionCallError(ChatError):
    """函数调用错误"""
    pass

class LLMError(ChatError):
    """大模型调用错误"""
    pass

class ToolLoadError(ChatError):
    """工具加载错误"""
    pass