from tts import StreamingTTS, get_secure_config
import time
# 从环境变量加载安全配置（自动格式化API密钥）
config = get_secure_config()
tts = StreamingTTS(config=config)

try:
    # 发送TTS请求
    text = "你好，欢迎使用ChatEcho TTS系统！"
    request_id = tts.send_tts_request(text)
    print(f"开始播放: {request_id}")
    
    # 等待播放完成
    tts.wait_for_completion()
    time.sleep(3000)
    print("播放完成")
    
finally:
    # 关闭TTS系统
    tts.close()