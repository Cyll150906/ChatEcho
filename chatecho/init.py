import json
from .api_client import APIClient
from .config import Config

class ChatWithHistory:
    def __init__(self, system_prompt="你是一个有用的AI助手。"):
        self.api_client = APIClient()
        self.system_prompt = system_prompt
        self.conversation_history = []
        self._add_system_message()

    def add_user_message(self, content):
        self.conversation_history.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.conversation_history.append({"role": "assistant", "content": content})

    def _add_system_message(self):
        if self.system_prompt:
            if self.conversation_history and self.conversation_history[0].get("role") == "system":
                self.conversation_history.pop(0)
            self.conversation_history.insert(0, {"role": "system", "content": self.system_prompt})

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt
        self._add_system_message()

    def get_system_prompt(self):
        return self.system_prompt

    def clear_history(self, keep_system=True):
        if keep_system and self.system_prompt:
            self.conversation_history = []
            self._add_system_message()
        else:
            self.conversation_history = []

    def get_response(self, user_input):
        self.add_user_message(user_input)
        payload = {
            "model": Config.CHAT_MODEL,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "enable_thinking": False,
            "messages": self.conversation_history
        }
        return self.api_client.post("chat/completions", payload)

    def process_response(self, response):
        try:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
            return ""
        except Exception as e:
            print(f"\n处理响应时出错: {e}")
            return ""

    def check_text_meaning(self, text):
        temp_messages = [
            {"role": "system", "content": "你是一个文本意义判断和修复助手。请分析用户输入的文本：\n1. 如果文本语义完全正常，返回JSON: {\"has_meaning\": true, \"corrected_text\": \"原始文本\"}\n2. 如果文本有轻微问题但能理解意思，进行修复后返回JSON: {\"has_meaning\": true, \"corrected_text\": \"修复后的文本\"}\n3. 如果文本完全无意义（如纯噪音、无关内容），返回JSON: {\"has_meaning\": false, \"corrected_text\": \"猜测的正常对话内容\"}\n只返回JSON格式，不要其他内容。"},
            {"role": "user", "content": f"请分析这段文本：'{text}'"}
        ]
        payload = {
            "model": "internlm/internlm2_5-7b-chat",
            "stream": False,
            "max_tokens": 200,
            "temperature": 0.1,
            "messages": temp_messages
        }
        
        max_retries = 2
        for _ in range(max_retries):
            response = self.api_client.post("chat/completions", payload, timeout=8)
            if response:
                try:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    return json.loads(content)
                except (json.JSONDecodeError, KeyError):
                    continue
        return {"has_meaning": True, "corrected_text": text}

    def continue_last_response(self):
        if not self.conversation_history or len(self.conversation_history) < 2:
            return "我还没有之前的对话内容可以继续。"
        
        last_assistant_message = next((msg["content"] for msg in reversed(self.conversation_history) if msg.get("role") == "assistant"), None)

        if not last_assistant_message:
            return "我还没有之前的回复可以继续。"

        continue_prompt = f"请基于我刚才的回复继续说下去，保持话题和语调的连贯性。我刚才说的是：{last_assistant_message}"
        
        temp_history = self.conversation_history + [{"role": "user", "content": continue_prompt}]
        
        payload = {
            "model": "Tongyi-Zhiwen/QwenLong-L1-32B",
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "messages": temp_history
        }
        
        response = self.api_client.post("chat/completions", payload)
        if response:
            content = self.process_response(response)
            if content:
                self.add_assistant_message(content)
                return content
        return "抱歉，我无法继续之前的内容。"

    def generate_opening_greeting(self):
        try:
            with open("./start", 'r', encoding='utf-8') as f:
                greeting_prompt = f.read()
        except FileNotFoundError:
            greeting_prompt = "请作为一个友好的AI语音助手，生成一个简短的开场白来欢迎用户。开场白应该：1. 简洁明了（不超过50字）2. 友好热情 3. 提示用户可以开始对话。请直接返回开场白内容，不要其他解释。"

        temp_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": greeting_prompt}
        ]
        
        payload = {
            "model": "Qwen/Qwen3-8B",
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.8,
            "top_p": 0.9,
            "messages": temp_messages
        }
        
        response = self.api_client.post("chat/completions", payload)
        if response:
            content = self.process_response(response)
            if content:
                self.add_assistant_message(content)
                return content
        
        default_greeting = "你好！我是你的AI语音助手，很高兴为你服务。请问有什么我可以帮助你的吗？"
        self.add_assistant_message(default_greeting)
        return default_greeting

    def chat(self, user_input):
        response = self.get_response(user_input)
        
        if not response:
            return None
        
        assistant_response = self.process_response(response)
        
        if assistant_response:
            self.add_assistant_message(assistant_response)
            print(assistant_response)
            return assistant_response
        else:
            print("\n❌ 未收到有效回复")
            return None

if __name__ == "__main__":
    chat = ChatWithHistory()
    while True:
        user_input = input("\n您: ").strip()
        if user_input.lower() in ['/quit', '/exit']:
            break
        chat.chat(user_input)