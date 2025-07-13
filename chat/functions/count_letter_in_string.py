"""字符串处理函数用于计算字母数量。

此模块提供用于计算字符串中特定字母出现次数的count_letter_in_string函数。
"""


def count_letter_in_string(a: str, b: str) -> str:
    """Count the number of occurrences of a letter in a string.
    
    Args:
        a: The source string to search in
        b: The letter to count (should be a single character)
        
    Returns:
        A string describing the count result
        
    Raises:
        TypeError: If either argument is not a string
        ValueError: If the letter parameter is not a single character
        
    Examples:
        >>> count_letter_in_string('hello', 'l')
        "The letter 'l' appears 2 times in the string."
        >>> count_letter_in_string('Python', 'y')
        "The letter 'y' appears 1 times in the string."
        >>> count_letter_in_string('test', 'x')
        "The letter 'x' appears 0 times in the string."
        >>> count_letter_in_string('HELLO', 'l')
        "The letter 'l' appears 2 times in the string."
    """
    if not isinstance(a, str):
        raise TypeError("First argument must be a string")
    if not isinstance(b, str):
        raise TypeError("Second argument must be a string")
    if len(b) != 1:
        raise ValueError("Letter parameter must be a single character")
    
    # Convert to lowercase for case-insensitive counting
    string = a.lower()
    letter = b.lower()
    
    count = string.count(letter)
    return f"The letter '{letter}' appears {count} times in the string."