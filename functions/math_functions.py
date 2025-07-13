"""数学计算函数。"""


def add(a: float, b: float) -> float:
    """计算两个数的和。
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两数之和
    """
    return a + b


def multiply(a: float, b: float) -> float:
    """计算两个数的乘积。
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两数之积
    """
    return a * b


def subtract(a: float, b: float) -> float:
    """计算两个数的差。
    
    Args:
        a: 被减数
        b: 减数
        
    Returns:
        两数之差
    """
    return a - b


def divide(a: float, b: float) -> float:
    """计算两个数的商。
    
    Args:
        a: 被除数
        b: 除数
        
    Returns:
        两数之商
        
    Raises:
        ValueError: 当除数为0时
    """
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b


def compare(a: float, b: float) -> str:
    """比较两个数的大小。
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        比较结果的描述
    """
    if a > b:
        return f'{a} 大于 {b}'
    elif a < b:
        return f'{b} 大于 {a}'
    else:
        return f'{a} 等于 {b}'