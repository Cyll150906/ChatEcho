"""字符串处理函数。"""


def count_letter_in_string(text: str, letter: str) -> str:
    """统计字符串中指定字母的出现次数。
    
    Args:
        text: 源字符串
        letter: 要统计的字母
        
    Returns:
        统计结果的描述
    """
    text_lower = text.lower()
    letter_lower = letter.lower()
    
    count = text_lower.count(letter_lower)
    return f"字母 '{letter}' 在字符串中出现了 {count} 次"


def reverse_string(text: str) -> str:
    """反转字符串。
    
    Args:
        text: 要反转的字符串
        
    Returns:
        反转后的字符串
    """
    return text[::-1]


def count_words(text: str) -> int:
    """统计字符串中的单词数量。
    
    Args:
        text: 要统计的字符串
        
    Returns:
        单词数量
    """
    words = text.strip().split()
    return len(words)


def to_uppercase(text: str) -> str:
    """将字符串转换为大写。
    
    Args:
        text: 要转换的字符串
        
    Returns:
        大写字符串
    """
    return text.upper()


def to_lowercase(text: str) -> str:
    """将字符串转换为小写。
    
    Args:
        text: 要转换的字符串
        
    Returns:
        小写字符串
    """
    return text.lower()


def find_substring(text: str, substring: str) -> str:
    """在字符串中查找子字符串。
    
    Args:
        text: 源字符串
        substring: 要查找的子字符串
        
    Returns:
        查找结果的描述
    """
    index = text.find(substring)
    if index != -1:
        return f"子字符串 '{substring}' 在位置 {index} 处找到"
    else:
        return f"子字符串 '{substring}' 未找到"