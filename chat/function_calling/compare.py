def compare(a: float, b: float):
    """比较两个数的大小"""
    print("compare被使用")
    if a > b:
        return f'{a} is greater than {b}'
    elif a < b:
        return f'{b} is greater than {a}'
    else:
        return f'{a} is equal to {b}'