"""TTS异常处理模块"""

class TTSError(Exception):
    """TTS基础异常类"""
    pass

class AudioError(TTSError):
    """音频相关异常"""
    pass

class AudioInitError(AudioError):
    """音频初始化异常"""
    pass

class AudioPlaybackError(AudioError):
    """音频播放异常"""
    pass

class RequestError(TTSError):
    """请求相关异常"""
    pass

class APIError(RequestError):
    """API请求异常"""
    pass

class NetworkError(RequestError):
    """网络连接异常"""
    pass

class AuthenticationError(APIError):
    """认证异常"""
    pass

class RateLimitError(APIError):
    """请求频率限制异常"""
    pass

class ConfigError(TTSError):
    """配置异常"""
    pass

class InvalidConfigError(ConfigError):
    """无效配置异常"""
    pass