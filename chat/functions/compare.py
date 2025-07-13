"""比较函数用于数学运算。

此模块提供用于比较两个数字的compare函数。
"""

from typing import Union


def compare(a: Union[int, float], b: Union[int, float]) -> str:
    """Compare two numbers and return which one is bigger.
    
    Args:
        a: First number to compare
        b: Second number to compare
        
    Returns:
        A string describing the comparison result
        
    Raises:
        TypeError: If either argument is not a number
        
    Examples:
        >>> compare(5, 3)
        '5 is greater than 3'
        >>> compare(2, 7)
        '7 is greater than 2'
        >>> compare(4, 4)
        '4 is equal to 4'
        >>> compare(3.14, 2.71)
        '3.14 is greater than 2.71'
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    
    if a > b:
        return f'{a} is greater than {b}'
    elif a < b:
        return f'{b} is greater than {a}'
    else:
        return f'{a} is equal to {b}'