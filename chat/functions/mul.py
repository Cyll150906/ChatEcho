"""乘法函数用于数学运算。

此模块提供用于计算两个数字乘积的mul函数。
"""

from typing import Union


def mul(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Calculate the product of two numbers.
    
    Args:
        a: First number to multiply
        b: Second number to multiply
        
    Returns:
        The product of a and b
        
    Raises:
        TypeError: If either argument is not a number
        
    Examples:
        >>> mul(2, 3)
        6
        >>> mul(2.5, 4)
        10.0
        >>> mul(-2, 3)
        -6
        >>> mul(0, 100)
        0
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    
    return a * b