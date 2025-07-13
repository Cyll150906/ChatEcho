"""Chat module exceptions."""


class ChatError(Exception):
    """Base exception for chat module."""
    pass


class ConfigError(ChatError):
    """Configuration related errors."""
    pass


class FunctionLoadError(ChatError):
    """Function loading related errors."""
    pass


class APIError(ChatError):
    """API related errors."""
    pass


class ArgumentParsingError(ChatError):
    """Function argument parsing errors."""
    pass