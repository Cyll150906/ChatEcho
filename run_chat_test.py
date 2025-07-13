#!/usr/bin/env python3
import os, sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from chat import ChatBot, setup_logging

setup_logging(level="INFO")

print("🤖 Testing ChatBot...")
try:
    # 现在ChatBot会自动从环境变量加载配置，无需手动检查API密钥
    chatbot = ChatBot()
    result = chatbot.function_call_playground("用中文回答：strawberry中有多少个r?")
    print(f"✅ Result: {result}")
except Exception as e:
    sys.exit(f"❌ Error: {e}")