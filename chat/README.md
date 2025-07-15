# Chat 模块

这是一个基于大模型的聊天模块，支持函数调用功能。

## 模块结构

```
chat/
├── __init__.py              # 模块初始化文件
├── README.md               # 模块说明文档
├── llm_client.py           # 大模型对话模块
├── function_caller.py      # 函数调用管理模块
├── core.py                 # 主要聊天模块
├── function_calling/       # 被调用函数模块
│   ├── __init__.py
│   ├── add.py             # 加法函数
│   ├── mul.py             # 乘法函数
│   ├── compare.py         # 比较函数
│   └── count_letter_in_string.py  # 字符统计函数
└── tools/                  # 函数配置文件夹
    ├── add.json
    ├── mul.json
    ├── compare.json
    └── count_letter_in_string.json
```

## 主要组件

### 1. 大模型对话模块 (llm_client.py)
- `LLMClient`: 封装OpenAI客户端，提供聊天完成功能

### 2. 函数调用模块 (function_caller.py)
- `FunctionCaller`: 管理函数配置加载和函数调用执行
- 自动从 `tools/` 目录加载所有 `.json` 配置文件
- 支持动态调用 `function_calling.functions` 模块中的函数

### 3. 被调用函数模块 (function_calling/)
- 每个函数都有独立的Python文件
- 支持动态导入，调用方式为 `function_calling.函数名`
- 当前支持的函数：
  - `function_calling.add`: 计算两个数的和
  - `function_calling.mul`: 计算两个数的乘积
  - `function_calling.compare`: 比较两个数的大小
  - `function_calling.count_letter_in_string`: 统计字符串中字母出现次数

### 4. 工具配置 (tools/)
- 每个函数对应一个独立的 JSON 配置文件
- 定义函数的名称、描述和参数规范

## 使用示例

### 基本使用

```python
from chat.core import ChatBot
from chat.config import ChatConfig
from chat.logging_config import setup_logging

# 设置日志（可选）
setup_logging(level="INFO")

# 方法1: 使用环境变量（推荐）
chatbot = ChatBot()

# 方法2: 直接传入API密钥
chatbot = ChatBot(api_key="your_api_key_here")

# 方法3: 使用配置对象
config = ChatConfig(api_key="your_api_key_here", base_url="https://api.siliconflow.cn/v1")
chatbot = ChatBot(config=config)

# 进行对话（支持连续对话和记忆功能）
response = chatbot.chat("用中文回答：strawberry中有多少个r?")
print(response)  # 输出: 在单词 "strawberry" 中，字母 "r" 出现了 3 次。

# 继续对话，ChatBot会记住之前的对话内容
response = chatbot.chat("那banana中有多少个a?")
print(response)  # ChatBot会基于之前的对话上下文回答

# 使用function_call_playground方法（完全参照fuc_call.py实现）
response = chatbot.function_call_playground("用中文回答：strawberry中有多少个r?")
print(response)
```

### 环境变量配置

支持以下环境变量（按优先级排序）：

```bash
# API密钥（任选其一）
CHAT_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
SILICONFLOW_API_KEY=your_api_key_here

# API基础URL（可选）
CHAT_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_BASE_URL=https://api.openai.com/v1

# 默认模型（可选）
CHAT_MODEL=deepseek-ai/DeepSeek-V3

# 日志级别（可选）
CHAT_LOG_LEVEL=INFO
```

### 连续对话和记忆管理

ChatBot现在支持连续对话和记忆功能，可以在多轮对话中保持上下文：

```python
from chat.core import ChatBot

chatbot = ChatBot()

# 第一轮对话
response1 = chatbot.chat("我叫张三，今年25岁")
print(response1)

# 第二轮对话 - ChatBot会记住你的信息
response2 = chatbot.chat("我多大了？")
print(response2)  # ChatBot会回答：根据您之前提到的信息，您今年25岁。

# 查看对话历史
history = chatbot.get_history()
print(f"对话历史条数: {len(history)}")

# 获取对话摘要
summary = chatbot.get_conversation_summary()
print(summary)

# 清空对话历史
chatbot.clear_history()

# 设置最大对话历史长度（默认20轮）
chatbot.set_max_history_length(10)
```

#### 记忆管理功能

- **自动历史管理**: 当对话历史超过最大长度时，自动删除最早的对话
- **上下文保持**: 在函数调用过程中保持完整的对话上下文
- **历史查看**: 可以查看当前的对话历史
- **历史清空**: 可以手动清空对话历史重新开始
- **长度控制**: 可以设置最大对话历史长度，避免上下文过长

## 错误处理

模块提供了完整的异常处理机制：

```python
from chat.core import ChatBot
from chat.exceptions import ChatError, ConfigurationError, FunctionCallError

try:
    chatbot = ChatBot()
    response = chatbot.chat("你的问题")
    print(response)
except ConfigurationError as e:
    print(f"配置错误: {e}")
except FunctionCallError as e:
    print(f"函数调用错误: {e}")
except ChatError as e:
    print(f"聊天错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 日志配置

```python
from chat.logging_config import setup_logging

# 基本配置
setup_logging(level="INFO")

# 配置日志文件
setup_logging(level="DEBUG", log_file="chat.log")
```

## function_call_playground 方法

为了完全兼容原有的 `fuc_call.py` 实现，我们提供了 `function_call_playground` 方法，该方法完全参照 `fuc_call.py` 中的 `function_call_playground` 函数实现：

### 主要特点

1. **完全相同的实现逻辑**：直接使用 `eval()` 执行函数调用
2. **相同的模型配置**：第一次调用使用 `deepseek-ai/DeepSeek-V2.5`，第二次调用使用 `Qwen/Qwen2.5-7B-Instruct`
3. **相同的参数设置**：`temperature=0.01`, `top_p=0.95`, `stream=False`
4. **相同的调试输出**：打印原始响应、函数结果和消息历史

### 使用示例

```python
from chat.core import ChatBot

chatbot = ChatBot()

# 测试用例（与fuc_call.py中的prompts相同）
prompts = [
    "用中文回答：strawberry中有多少个r?", 
    "用中文回答：9.11和9.9，哪个小?"
]

for prompt in prompts:
    response = chatbot.function_call_playground(prompt)
    print(response)
```

### 与原始实现的对应关系

| fuc_call.py | chat模块 |
|-------------|----------|
| `function_call_playground(prompt)` | `chatbot.function_call_playground(prompt)` |
| 直接定义的函数 | `chat.function_calling` 模块中的函数 |
| 硬编码的 `tools` 列表 | 从 `tools/` 目录动态加载的配置 |
| `eval()` 执行函数 | 同样使用 `eval()` 执行函数 |
| 两次不同模型调用 | 完全相同的模型调用策略 |

## 添加新函数

1. 在 `function_calling/` 目录下创建新的Python文件（如 `new_function.py`）
2. 在文件中实现同名函数（如 `def new_function(...):`）
3. 在 `tools/` 目录下创建对应的 JSON 配置文件（如 `new_function.json`）
4. 重启应用，新函数将自动可用，调用方式为 `function_calling.new_function`

### 示例：添加减法函数

1. 创建 `function_calling/subtract.py`：
```python
def subtract(a: float, b: float) -> float:
    """计算两个数的差"""
    return a - b
```

2. 创建 `tools/subtract.json`：
```json
{
    "type": "function",
    "function": {
        "name": "subtract",
        "description": "Calculate the difference between two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "The first number"
                },
                "b": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["a", "b"]
        }
    }
}
```