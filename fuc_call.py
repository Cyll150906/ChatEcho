from openai import OpenAI
from pydantic import conbytes

client = OpenAI(
    api_key="sk-ilisodyqqyoevaczooibujphobvfhzeonqgpfzudinlcxurs", # 从https://cloud.siliconflow.cn/account/ak获取
    base_url="https://api.siliconflow.cn/v1"
)

def add(a: float, b: float):
    return a + b

def mul(a: float, b: float):
    return a * b

def compare(a: float, b: float):
    if a > b:
        return f'{a} is greater than {b}'
    elif a < b:
        return f'{b} is greater than {a}'
    else:
        return f'{a} is equal to {b}'

def count_letter_in_string(a: str, b: str):
    string = a.lower()
    letter = b.lower()
    
    count = string.count(letter)
    return(f"The letter '{letter}' appears {count} times in the string.")


tools = [
{
    'type': 'function',
    'function': {
        'name': 'add',
        'description': 'Compute the sum of two numbers',
        'parameters': {
            'type': 'object',
            'properties': {
                'a': {
                    'type': 'int',
                    'description': 'A number',
                },
                'b': {
                    'type': 'int',
                    'description': 'A number',
                },
            },
            'required': ['a', 'b'],
        },
    }
}, 
{
    'type': 'function',
    'function': {
        'name': 'mul',
        'description': 'Calculate the product of two numbers',
        'parameters': {
            'type': 'object',
            'properties': {
                'a': {
                    'type': 'int',
                    'description': 'A number',
                },
                'b': {
                    'type': 'int',
                    'description': 'A number',
                },
            },
            'required': ['a', 'b'],
        },
    }
},
{
    'type': 'function',
    'function': {
        'name': 'count_letter_in_string',
        'description': 'Count letter number in a string',
        'parameters': {
            'type': 'object',
            'properties': {
                'a': {
                    'type': 'str',
                    'description': 'source string',
                },
                'b': {
                    'type': 'str',
                    'description': 'letter',
                },
            },
            'required': ['a', 'b'],
        },
    }
},
{
    'type': 'function',
    'function': {
        'name': 'compare',
        'description': 'Compare two number, which one is bigger',
        'parameters': {
            'type': 'object',
            'properties': {
                'a': {
                    'type': 'float',
                    'description': 'A number',
                },
                'b': {
                    'type': 'float',
                    'description': 'A number',
                },
            },
            'required': ['a', 'b'],
        },
    }
}
]

def function_call_playground(prompt):
    messages = [{'role': 'user', 'content': prompt}]
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages = messages,
        temperature=0.01,
        top_p=0.95,
        stream=False,
        tools=tools)

    # 检查是否有tool_calls
    if not response.choices[0].message.tool_calls:
        return response.choices[0].message.content or "No response content"
    
    func1_name = response.choices[0].message.tool_calls[0].function.name
    func1_args = response.choices[0].message.tool_calls[0].function.arguments
    
    # 解析JSON格式的参数
    import json
    import re
    
    # 清理参数字符串，移除markdown代码块和特殊字符
    cleaned_args = func1_args.strip()
    # 移除markdown代码块标记
    cleaned_args = re.sub(r'```[^`]*```', '', cleaned_args)
    # 移除特殊的工具调用标记
    cleaned_args = re.sub(r'<｜[^｜]*｜>', '', cleaned_args)
    # 移除所有换行符和多余空格
    cleaned_args = re.sub(r'\s+', ' ', cleaned_args)
    cleaned_args = cleaned_args.strip()
    
    # 尝试提取JSON部分
    json_match = re.search(r'\{[^}]+\}', cleaned_args)
    if json_match:
        cleaned_args = json_match.group(0)
    
    try:
        func1_args_dict = json.loads(cleaned_args)
        func1_out = eval(f'{func1_name}(**{func1_args_dict})')
    except json.JSONDecodeError as e:
        print(f"Error parsing arguments: {e}")
        return "Error: Invalid function arguments format"
    # print(func1_out)

    messages.append(response.choices[0].message)
    messages.append({
        'role': 'tool',
        'content': f'{func1_out}',
        'tool_call_id': response.choices[0].message.tool_calls[0].id
    })
    # print(messages)
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2.5",
        messages=messages,
        temperature=0.01,
        top_p=0.95,
        stream=False,
        tools=tools)
    
    # 处理响应内容
    content = response.choices[0].message.content
    print(content)

    if content:
        # 如果内容包含特殊的工具调用格式，则清理它
        if '<｜tool▁calls▁begin｜>' in content:
            # 这种情况下，直接返回函数执行的结果
            return str(func1_out)
        else:
            return content
    elif response.choices[0].message.tool_calls:
        return f"Tool call: {response.choices[0].message.tool_calls[0].function.name}"
    else:
        return "No response content"
  
prompts = [
    "用中文回答：strawberry中有多少个r?", 
    "用中文回答：9.11和9.9，哪个小?"
]

for prompt in prompts:
    print(function_call_playground(prompt))