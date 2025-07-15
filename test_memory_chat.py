#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ChatBot的连续对话和记忆功能
"""

from chat.core import ChatBot
from chat.logging_config import setup_logging

def test_memory_functionality():
    """测试记忆功能"""
    print("=== ChatBot 连续对话和记忆功能测试 ===")
    
    # 设置日志
    setup_logging(level="INFO")
    
    # 创建ChatBot实例
    chatbot = ChatBot()
    
    print("\n1. 基本记忆测试")
    print("-" * 40)
    
    # 第一轮对话 - 建立记忆
    response1 = chatbot.chat("我叫张三，今年25岁，是一名程序员")
    print(f"用户: 我叫张三，今年25岁，是一名程序员")
    print(f"助手: {response1}")
    
    # 第二轮对话 - 测试记忆
    response2 = chatbot.chat("我多大了？")
    print(f"\n用户: 我多大了？")
    print(f"助手: {response2}")
    
    # 第三轮对话 - 测试记忆
    response3 = chatbot.chat("我的职业是什么？")
    print(f"\n用户: 我的职业是什么？")
    print(f"助手: {response3}")
    
    print("\n2. 对话历史管理测试")
    print("-" * 40)
    
    # 查看对话历史
    history = chatbot.get_history()
    print(f"当前对话历史条数: {len(history)}")
    
    # 获取对话摘要
    summary = chatbot.get_conversation_summary()
    print(f"对话摘要: {summary}")
    
    print("\n3. 函数调用记忆测试")
    print("-" * 40)
    
    # 测试函数调用是否保持记忆
    response4 = chatbot.chat("请计算我的年龄加上10是多少？")
    print(f"用户: 请计算我的年龄加上10是多少？")
    print(f"助手: {response4}")
    
    print("\n4. 历史长度管理测试")
    print("-" * 40)
    
    # 设置较小的历史长度
    chatbot.set_max_history_length(4)
    print("设置最大历史长度为4")
    
    # 添加更多对话
    for i in range(3):
        response = chatbot.chat(f"这是第{i+1}条新消息")
        print(f"用户: 这是第{i+1}条新消息")
        print(f"助手: {response}")
    
    # 查看历史是否被正确管理
    final_history = chatbot.get_history()
    print(f"\n管理后的对话历史条数: {len(final_history)}")
    
    # 测试早期记忆是否还存在
    response5 = chatbot.chat("我叫什么名字？")
    print(f"\n用户: 我叫什么名字？")
    print(f"助手: {response5}")
    
    print("\n5. 清空历史测试")
    print("-" * 40)
    
    # 清空历史
    chatbot.clear_history()
    print("已清空对话历史")
    
    # 测试清空后的对话
    response6 = chatbot.chat("我叫什么名字？")
    print(f"用户: 我叫什么名字？")
    print(f"助手: {response6}")
    
    final_summary = chatbot.get_conversation_summary()
    print(f"最终对话摘要: {final_summary}")
    
    print("\n=== 测试完成 ===")

def test_function_call_with_memory():
    """测试函数调用与记忆的结合"""
    print("\n=== 函数调用记忆测试 ===")
    
    chatbot = ChatBot()
    
    # 建立数字记忆
    response1 = chatbot.chat("我有5个苹果")
    print(f"用户: 我有5个苹果")
    print(f"助手: {response1}")
    
    # 使用函数调用基于记忆进行计算
    response2 = chatbot.chat("如果我再买3个苹果，总共有多少个？")
    print(f"\n用户: 如果我再买3个苹果，总共有多少个？")
    print(f"助手: {response2}")
    
    # 继续基于结果进行对话
    response3 = chatbot.chat("那我现在总共有多少个苹果？")
    print(f"\n用户: 那我现在总共有多少个苹果？")
    print(f"助手: {response3}")

if __name__ == "__main__":
    try:
        test_memory_functionality()
        test_function_call_with_memory()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()