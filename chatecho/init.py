import requests
import json

class ChatWithHistory:
    def __init__(self, system_prompt="你是一个有用的AI助手。"):
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer sk-oyxoqrxbymcizdfmfuzdxtudualgftadigummmozhhpdjamu",
            "Content-Type": "application/json"
        }
        self.system_prompt = system_prompt
        self.conversation_history = []
        self._add_system_message()
    
    def add_user_message(self, content):
        """添加用户消息到对话历史"""
        self.conversation_history.append({
            "role": "user",
            "content": content
        })
    
    def add_assistant_message(self, content):
        """添加助手回复到对话历史"""
        self.conversation_history.append({
            "role": "assistant",
            "content": content
        })
    
    def _add_system_message(self):
        """添加系统消息到对话历史开头"""
        if self.system_prompt:
            # 如果已有系统消息，先移除
            if self.conversation_history and self.conversation_history[0].get("role") == "system":
                self.conversation_history.pop(0)
            # 在开头插入新的系统消息
            self.conversation_history.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })
    
    def set_system_prompt(self, system_prompt):
        """设置系统提示词"""
        self.system_prompt = system_prompt
        self._add_system_message()
    
    def get_system_prompt(self):
        """获取当前系统提示词"""
        return self.system_prompt
    
    def clear_history(self, keep_system=True):
        """清空对话历史"""
        if keep_system and self.system_prompt:
            self.conversation_history = []
            self._add_system_message()
        else:
            self.conversation_history = []
    
    def get_response(self, user_input):
        """发送请求并获取完整响应"""
        self.add_user_message(user_input)
        
        payload = {
            "model": "Qwen/Qwen3-30B-A3B",
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "enable_thinking": False,
            "messages": self.conversation_history
        }
        
        try:
            response = requests.post(
                self.url, 
                json=payload, 
                headers=self.headers, 
                timeout=30
            )
            
            if response.status_code != 200:
                return None, f"请求失败，状态码: {response.status_code}"
            
            return response, None
            
        except Exception as e:
            return None, f"请求异常: {e}"
    
    def process_response(self, response):
        """处理响应并返回完整内容"""
        try:
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    return content
            
            return ""
            
        except Exception as e:
            print(f"\n处理响应时出错: {e}")
            return ""
    
    def check_text_meaning(self, text):
        """判断文本是否具有实际意义，并返回JSON格式结果"""
        # 创建临时对话历史，不影响主对话
        temp_messages = [
            {
                "role": "system",
                "content": "你是一个文本意义判断和修复助手。请分析用户输入的文本：\n1. 如果文本语义完全正常，返回JSON: {\"has_meaning\": true, \"corrected_text\": \"原始文本\"}\n2. 如果文本有轻微问题但能理解意思，进行修复后返回JSON: {\"has_meaning\": true, \"corrected_text\": \"修复后的文本\"}\n3. 如果文本完全无意义（如纯噪音、无关内容），返回JSON: {\"has_meaning\": false, \"corrected_text\": \"猜测的正常对话内容\"}\n只返回JSON格式，不要其他内容。"
            },
            {
                "role": "user",
                "content": f"请分析这段文本：'{text}'"
            }
        ]
        
        payload = {
            "model": "internlm/internlm2_5-7b-chat",
            "stream": False,
            "max_tokens": 200,
            "temperature": 0.1,
            "messages": temp_messages
        }
        
        # 重试机制
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=8  # 减少超时时间
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        content = response_data['choices'][0]['message']['content'].strip()
                        
                        # 尝试解析JSON
                        try:
                            import json
                            result = json.loads(content)
                            return result
                        except json.JSONDecodeError:
                            # 如果解析失败，尝试提取关键信息
                            if "false" in content.lower():
                                return {"has_meaning": False, "corrected_text": "请问有什么我可以帮助您的吗？"}
                            else:
                                return {"has_meaning": True, "corrected_text": text}
                
                # 如果状态码不是200，继续重试
                if attempt < max_retries - 1:
                    print(f"⚠️ 意义判断请求失败 (状态码: {response.status_code})，正在重试...")
                    continue
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ 意义判断请求超时，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    print("❌ 意义判断请求多次超时，跳过判断")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ 意义判断出错: {e}，正在重试...")
                    continue
                else:
                    print(f"❌ 意义判断出错: {e}")
        
        # 所有重试都失败，默认返回原始文本
        return {"has_meaning": True, "corrected_text": text}
    
    def continue_last_response(self):
        """基于上一次回复继续生成内容"""
        if not self.conversation_history or len(self.conversation_history) < 2:
            return "我还没有之前的对话内容可以继续。"
        
        # 找到最后一次助手回复
        last_assistant_message = None
        for message in reversed(self.conversation_history):
            if message.get("role") == "assistant":
                last_assistant_message = message.get("content", "")
                break
        
        if not last_assistant_message:
            return "我还没有之前的回复可以继续。"
        
        # 创建继续生成的请求
        continue_prompt = f"请基于我刚才的回复继续说下去，保持话题和语调的连贯性。我刚才说的是：{last_assistant_message}"
        
        # 临时添加继续请求
        temp_history = self.conversation_history.copy()
        temp_history.append({
            "role": "user",
            "content": continue_prompt
        })
        
        payload = {
            "model": "Tongyi-Zhiwen/QwenLong-L1-32B",
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "messages": temp_history
        }
        
        try:
            response = requests.post(
                self.url, 
                json=payload, 
                headers=self.headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    # 将继续的内容添加到对话历史
                    self.add_assistant_message(content)
                    return content
            
            return "抱歉，我无法继续之前的内容。"
            
        except Exception as e:
            print(f"❌ 继续生成出错: {e}")
            return "抱歉，继续生成时出现了问题。"
    
    def generate_opening_greeting(self):
        """生成开场白"""
        with open("./start",'r',encoding='utf-8') as f :
            start=f.read()
            greeting_prompt = start
        print(greeting_prompt)
        # greeting_prompt = "请作为一个友好的AI语音助手，生成一个简短的开场白来欢迎用户。开场白应该：1. 简洁明了（不超过50字）2. 友好热情 3. 提示用户可以开始对话。请直接返回开场白内容，不要其他解释。"
        
        # 创建临时对话历史，不影响主对话
        temp_messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": greeting_prompt
            }
        ]
        
        payload = {
            "model": "Qwen/Qwen3-8B",
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.8,
            "top_p": 0.9,
            "messages": temp_messages
        }
        
        try:
            response = requests.post(
                self.url, 
                json=payload, 
                headers=self.headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content'].strip()
                    # 将开场白添加到对话历史
                    self.add_assistant_message(content)
                    return content
            
            # 如果API调用失败，返回默认开场白
            default_greeting = "你好！我是你的AI语音助手，很高兴为你服务。请问有什么我可以帮助你的吗？"
            self.add_assistant_message(default_greeting)
            return default_greeting
            
        except Exception as e:
            print(f"❌ 生成开场白时出错: {e}")
            # 返回默认开场白
            default_greeting = "你好！我是你的AI语音助手，很高兴为你服务。请问有什么我可以帮助你的吗？"
            self.add_assistant_message(default_greeting)
            return default_greeting
    
    def chat(self, user_input):
        """进行一轮对话"""
        response, error = self.get_response(user_input)
        
        if error:
            print(f"❌ {error}")
            return None
        
        assistant_response = self.process_response(response)
        
        if assistant_response:
            self.add_assistant_message(assistant_response)
            print(assistant_response)
            return assistant_response
        else:
            print("\n❌ 未收到有效回复")
            return None

# 使用示例
if __name__ == "__main__":
    chat = ChatWithHistory()
    
    while True:
        user_input = input("\n您: ").strip()
        if user_input.lower() in ['/quit', '/exit']:
            break
        
        chat.chat(user_input)