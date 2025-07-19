"""XML Report Parser for handling XML files without root nodes.

这个模块提供了专门用于处理无根节点XML文件的解析器。
许多XML报告文件缺少根节点，导致标准XML解析器无法直接处理。
本解析器通过自动添加根节点包装器来解决这个问题。

主要功能：
- 自动检测和处理无根节点的XML文件
- 添加根节点包装器以确保XML格式正确
- 提供安全的错误处理机制
- 支持UTF-8编码的XML文件

使用示例：
    parser = XMLReportParser()
    root = parser.parse_file('report.xml')
    if root is not None:
        # 处理解析后的XML数据
        pass
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Union


class XMLReportParser:
    """XML报告文件解析器，专门处理缺少根节点的XML文件。
    
    这个解析器能够自动处理格式不规范的XML报告文件，通过添加根节点包装器
    使其符合标准XML格式，从而能够被正常解析和处理。
    
    Attributes:
        root (Optional[ET.Element]): 解析后的XML根元素，初始为None
    
    Note:
        解析器会自动检测XML声明并在适当位置插入根节点标签。
        支持UTF-8编码的XML文件，确保中文内容正确处理。
    """
    
    def __init__(self) -> None:
        """初始化XML解析器。
        
        初始化时root属性为None，需要调用parse_file方法进行文件解析。
        """
        self.root: Optional[ET.Element] = None
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[ET.Element]:
        """解析XML文件，自动添加根节点包装器。
        
        这个方法会读取指定的XML文件，检测是否缺少根节点，如果缺少则自动添加
        根节点包装器，然后进行解析。解析成功后会将结果存储在self.root中。
        
        Args:
            file_path (Union[str, Path]): XML文件的路径，支持字符串或Path对象
            
        Returns:
            Optional[ET.Element]: 解析成功返回XML根元素，失败返回None
            
        Raises:
            FileNotFoundError: 当指定的文件不存在时抛出
            ET.ParseError: 当XML格式错误无法解析时抛出
            
        Note:
            - 支持UTF-8编码的XML文件
            - 自动处理XML声明行
            - 提供详细的错误信息输出
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read the original file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add root node wrapper
            wrapped_content = self._add_root_wrapper(content)
            
            # Parse the wrapped XML
            self.root = ET.fromstring(wrapped_content)
            return self.root
            
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return None
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None
    
    def _add_root_wrapper(self, content: str) -> str:
        """为XML内容添加根节点包装器。
        
        这个私有方法负责检测XML内容的结构，并在适当的位置添加根节点标签。
        如果存在XML声明行，会在声明行之后插入根开始标签，否则在内容开头插入。
        
        Args:
            content (str): 原始的XML内容字符串，可能缺少根节点
            
        Returns:
            str: 添加了根节点包装器的完整XML内容
            
        Note:
            - 自动检测XML声明行（<?xml version=...?>）
            - 在文件末尾添加根结束标签
            - 保持原有的换行格式
        """
        lines = content.strip().split('\n')
        
        # Find the first line (XML declaration) and insert root after it
        if lines and lines[0].startswith('<?xml'):
            # Insert root opening tag after XML declaration
            lines.insert(1, '<root>')
        else:
            # Insert root opening tag at the beginning
            lines.insert(0, '<root>')
        
        # Add closing root tag at the end
        lines.append('</root>')
        
        return '\n'.join(lines)
    
    def get_root(self) -> Optional[ET.Element]:
        """获取解析后的XML根元素。
        
        Returns:
            Optional[ET.Element]: 如果已成功解析文件则返回根元素，否则返回None
            
        Note:
            需要先调用parse_file方法进行文件解析，否则返回None
        """
        return self.root