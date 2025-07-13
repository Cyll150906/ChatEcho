"""聊天模块异常类。

包含以下异常类：
- ChatError: 聊天相关错误的基类
- ConfigError: 配置相关错误
- FunctionLoadError: 函数加载错误
- APIError: API调用错误
- ArgumentParsingError: 参数解析错误。
"""


class ChatError(Exception):
    """Base exception for chat module."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """Initialize ChatError.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> dict:
        """Convert error to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ConfigError(ChatError):
    """Configuration related errors."""
    
    def __init__(self, message: str, config_key: str = None, config_file: str = None):
        """Initialize ConfigError.
        
        Args:
            message: Error message
            config_key: The configuration key that caused the error
            config_file: The configuration file path
        """
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key
        self.config_file = config_file
        if config_key:
            self.details["config_key"] = config_key
        if config_file:
            self.details["config_file"] = config_file


class FunctionLoadError(ChatError):
    """Function loading related errors."""
    
    def __init__(self, message: str, function_name: str = None, file_path: str = None, 
                 original_error: Exception = None):
        """Initialize FunctionLoadError.
        
        Args:
            message: Error message
            function_name: Name of the function that failed to load
            file_path: Path to the file containing the function
            original_error: The original exception that caused this error
        """
        super().__init__(message, "FUNCTION_LOAD_ERROR")
        self.function_name = function_name
        self.file_path = file_path
        self.original_error = original_error
        
        if function_name:
            self.details["function_name"] = function_name
        if file_path:
            self.details["file_path"] = file_path
        if original_error:
            self.details["original_error"] = str(original_error)
            self.details["original_error_type"] = type(original_error).__name__


class APIError(ChatError):
    """API related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None,
                 request_id: str = None):
        """Initialize APIError.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from the API
            request_id: Request ID for tracking
        """
        super().__init__(message, "API_ERROR")
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id
        
        if status_code:
            self.details["status_code"] = status_code
        if response_data:
            self.details["response_data"] = response_data
        if request_id:
            self.details["request_id"] = request_id
    
    @property
    def is_rate_limit_error(self) -> bool:
        """Check if this is a rate limit error."""
        return self.status_code == 429
    
    @property
    def is_authentication_error(self) -> bool:
        """Check if this is an authentication error."""
        return self.status_code in (401, 403)
    
    @property
    def is_server_error(self) -> bool:
        """Check if this is a server error."""
        return self.status_code and self.status_code >= 500


class ArgumentParsingError(ChatError):
    """Function argument parsing errors."""
    
    def __init__(self, message: str, function_name: str = None, argument_name: str = None,
                 expected_type: str = None, received_value: str = None):
        """Initialize ArgumentParsingError.
        
        Args:
            message: Error message
            function_name: Name of the function with argument parsing error
            argument_name: Name of the problematic argument
            expected_type: Expected type of the argument
            received_value: The value that was received
        """
        super().__init__(message, "ARGUMENT_PARSING_ERROR")
        self.function_name = function_name
        self.argument_name = argument_name
        self.expected_type = expected_type
        self.received_value = received_value
        
        if function_name:
            self.details["function_name"] = function_name
        if argument_name:
            self.details["argument_name"] = argument_name
        if expected_type:
            self.details["expected_type"] = expected_type
        if received_value is not None:
            self.details["received_value"] = str(received_value)