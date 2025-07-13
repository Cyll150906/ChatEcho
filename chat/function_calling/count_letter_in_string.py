def count_letter_in_string(a: str, b: str):
    """统计字符串中某个字母的出现次数"""
    string = a.lower()
    letter = b.lower()
    
    count = string.count(letter)
    print("函数被使用")
    return f"The letter '{letter}' appears {count} times in the string."