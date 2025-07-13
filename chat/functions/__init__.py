"""聊天功能包。

此包包含与工具定义JSON文件一一对应的单独功能模块。每个模块包含一个具有
全面文档和类型注解的单一函数。

Modules:
    add: 用于数学运算的加法函数
    mul: 用于数学运算的乘法函数
    compare: 用于数学运算的比较函数
    count_letter_in_string: 用于计算字母的字符串处理函数
"""

from .add import add
from .compare import compare
from .count_letter_in_string import count_letter_in_string
from .mul import mul

__all__ = [
    "add",
    "compare",
    "count_letter_in_string",
    "mul",
]