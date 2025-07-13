"""聊天工具包。

此包提供从JSON文件加载工具定义的实用程序，支持单工具文件和多工具文件的向后兼容性。
"""

import json
import os
from typing import Any, Dict, List


def load_tool_from_json(json_file_path: str) -> Dict[str, Any]:
    """Load a single tool from a JSON file.
    
    Args:
        json_file_path: Path to the JSON file containing a single tool definition
        
    Returns:
        Single tool definition
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is malformed
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tools_from_json(json_file_path: str) -> List[Dict[str, Any]]:
    """Load tools from a JSON file (backward compatibility).
    
    Args:
        json_file_path: Path to the JSON file containing tool definitions
        
    Returns:
        List of tool definitions
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is malformed
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle both single tool and array of tools
        if isinstance(data, list):
            return data
        else:
            return [data]


def load_all_tools() -> List[Dict[str, Any]]:
    """Load all tools from the tools directory.
    
    Returns:
        List of all tool definitions
    """
    tools = []
    tools_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(tools_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(tools_dir, filename)
            try:
                tool = load_tool_from_json(file_path)
                tools.append(tool)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Failed to load tool from {filename}: {e}")
    
    return tools


__all__ = [
    "load_tool_from_json",
    "load_tools_from_json",
    "load_all_tools",
]