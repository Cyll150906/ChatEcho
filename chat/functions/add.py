"""加法函数用于数学运算。

此模块提供用于计算两个数字之和的add函数。
"""

from typing import Union


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Compute the sum of two numbers.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        The sum of a and b
        
    Raises:
        TypeError: If either argument is not a number
        
    Examples:
        >>> add(2, 3)
        5
        >>> add(2.5, 3.7)
        6.2
        >>> add(-1, 1)
        0
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    
    return a + b