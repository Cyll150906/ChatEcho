#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatBot连续对话和记忆功能使用示例
"""

from chat.core import ChatBot
from chat.logging_config import setup_logging

def main():
    """主函数 - 演示连续对话功能"""
    print("=== ChatBot 连续对话示例 ===")
    
    # 设置日志（可选）
    setup_logging(level="INFO")
    
    # 创建ChatBot实例
    chatbot = ChatBot()
    
    print("\n开始对话（输入 'quit吧' 退出，'clear' 清空历史，'history' 查看历史）")
    print("-" * 50)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()
            
            # 处理特殊命令
            if user_input.lower() == 'quit':
                print("再见！")
                break
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                print("对话历史已清空")
                continue
            elif user_input.lower() == 'history':
                summary = chatbot.get_conversation_summary()
                print(f"对话摘要: {summary}")
                continue
            elif user_input.lower() == 'help':
                print("可用命令:")
                print("  quit - 退出程序")
                print("  clear - 清空对话历史")
                print("  history - 查看对话摘要")
                print("  help - 显示帮助")
                continue
            elif not user_input:
                continue
            
            # 进行对话
            response = chatbot.chat(user_input)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            continue
    
    # 显示最终统计
    final_summary = chatbot.get_conversation_summary()
    print(f"\n最终对话统计: {final_summary}")

def demo_conversation():
    """演示对话示例"""
    print("\n=== 自动演示对话 ===")
    
    chatbot = ChatBot()
    
    # 演示对话序列
    conversations = [
        "我叫李明，是一名数据科学家",
        "我今年28岁",
        "我的爱好是机器学习和深度学习",
        "我多大了？",
        "我的职业是什么？",
        "我的爱好有哪些？",
        "请计算我的年龄乘以2是多少？",
        "那结果再加上10呢？"
    ]
    
    for i, prompt in enumerate(conversations, 1):
        print(f"\n第{i}轮对话:")
        print(f"用户: {prompt}")
        
        response = chatbot.chat(prompt)
        print(f"AI: {response}")
        
        # 显示当前对话统计
        summary = chatbot.get_conversation_summary()
        print(f"当前统计: {summary}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    try:
        # 可以选择运行交互式对话或自动演示
        import sys
        
        if len(sys.argv) > 1 and sys.argv[1] == "demo":
            demo_conversation()
        else:
            main()
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()