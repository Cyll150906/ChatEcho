"""ASR异常模块

定义ASR系统的异常类型，提供详细的错误信息和处理建议。
"""


class ASRException(Exception):
    """ASR系统基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, suggestions: list = None):
        super().__init__(message)
        self.error_code = error_code
        self.suggestions = suggestions or []
    
    def __str__(self):
        result = super().__str__()
        if self.error_code:
            result = f"[{self.error_code}] {result}"
        if self.suggestions:
            result += "\n建议解决方案:\n" + "\n".join(f"  - {s}" for s in self.suggestions)
        return result


class ASRConfigurationError(ASRException):
    """ASR配置错误"""
    
    def __init__(self, message: str, config_key: str = None):
        suggestions = [
            "检查配置文件格式是否正确",
            "确认所有必需的配置项都已设置",
            "参考示例配置文件进行配置"
        ]
        if config_key:
            suggestions.insert(0, f"检查配置项 '{config_key}' 的值")
        
        super().__init__(message, "CONFIG_ERROR", suggestions)
        self.config_key = config_key


class ASRRecordingError(ASRException):
    """录音相关错误"""
    
    def __init__(self, message: str, device_info: dict = None):
        suggestions = [
            "检查麦克风是否正常连接",
            "确认音频设备权限已授予",
            "尝试重新启动音频服务",
            "检查是否有其他程序占用音频设备"
        ]
        
        super().__init__(message, "RECORDING_ERROR", suggestions)
        self.device_info = device_info


class ASRTranscriptionError(ASRException):
    """转录相关错误"""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        suggestions = [
            "检查网络连接是否正常",
            "确认API密钥是否有效",
            "检查音频文件格式是否支持",
            "尝试重新发送请求"
        ]
        
        if status_code == 401:
            suggestions.insert(0, "检查API密钥是否正确配置")
        elif status_code == 429:
            suggestions.insert(0, "API调用频率过高，请稍后重试")
        elif status_code == 413:
            suggestions.insert(0, "音频文件过大，请压缩后重试")
        
        super().__init__(message, "TRANSCRIPTION_ERROR", suggestions)
        self.status_code = status_code
        self.response_text = response_text


class ASRAudioError(ASRException):
    """音频处理错误"""
    
    def __init__(self, message: str, file_path: str = None):
        suggestions = [
            "检查音频文件是否存在",
            "确认音频文件格式是否正确",
            "检查文件是否损坏",
            "尝试使用其他音频文件"
        ]
        
        super().__init__(message, "AUDIO_ERROR", suggestions)
        self.file_path = file_path


class ASRDeviceError(ASRException):
    """音频设备错误"""
    
    def __init__(self, message: str, device_index: int = None, available_devices: list = None):
        suggestions = [
            "检查音频设备是否正确连接",
            "确认设备驱动程序是否正常",
            "尝试使用默认音频设备",
            "重新启动应用程序"
        ]
        
        if available_devices:
            suggestions.append(f"可用设备列表: {available_devices}")
        
        super().__init__(message, "DEVICE_ERROR", suggestions)
        self.device_index = device_index
        self.available_devices = available_devices