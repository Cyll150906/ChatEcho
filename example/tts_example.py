"""TTS包使用示例"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts import (
    StreamingTTS, 
    AudioConfig, 
    APIConfig, 
    TTSConfig,
    generate_request_id,
    save_audio_to_file,
    format_duration
)

def basic_usage_example():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建TTS实例
    tts = StreamingTTS()
    
    try:
        # 发送TTS请求
        text = "这是一个基础的TTS测试示例。"
        request_id = tts.send_tts_request(text)
        print(f"发送请求: {request_id}")
        
        # 等待播放完成
        tts.wait_for_completion()
        print("播放完成")
        
    finally:
        # 关闭TTS系统
        tts.close()

def advanced_usage_example():
    """高级使用示例"""
    print("=== 高级使用示例 ===")
    
    # 自定义配置
    audio_config = AudioConfig(rate=48000, chunk=4096)
    api_config = APIConfig()
    config = TTSConfig(audio=audio_config, api=api_config)
    
    # 使用自定义配置创建TTS实例
    tts = StreamingTTS(
        format=config.audio.format,
        channels=config.audio.channels,
        rate=config.audio.rate,
        chunk=config.audio.chunk
    )
    
    try:
        # 设置API配置
        tts.set_api_config(
            api_url=config.api.url,
            api_key=config.api.key,
            default_model=config.api.default_model,
            default_voice=config.api.default_voice
        )
        
        # 发送多个请求
        texts = [
            "这是第一段测试文本。",
            "这是第二段测试文本。",
            "这是第三段测试文本。"
        ]
        
        request_ids = []
        for i, text in enumerate(texts, 1):
            request_id = generate_request_id(f"test_{i}")
            result_id = tts.send_tts_request(
                text=text,
                request_id=request_id,
                speed=1.2,
                gain=0.1
            )
            request_ids.append(result_id)
            print(f"发送请求 {i}: {result_id}")
            time.sleep(0.5)  # 间隔发送
        
        # 等待所有播放完成
        print("等待播放完成...")
        tts.wait_for_completion()
        print("所有音频播放完成")
        
    finally:
        tts.close()

def playback_control_example():
    """播放控制示例"""
    print("=== 播放控制示例 ===")
    
    tts = StreamingTTS()
    
    try:
        # 发送长文本请求
        long_text = "这是一段比较长的测试文本，用于演示播放控制功能。" * 5
        request_id = tts.send_tts_request(long_text)
        print(f"开始播放: {request_id}")
        
        # 播放2秒后暂停
        time.sleep(2)
        print("暂停播放")
        tts.pause()
        
        # 暂停2秒后恢复
        time.sleep(2)
        print("恢复播放")
        tts.resume()
        
        # 再播放2秒后停止
        time.sleep(2)
        print("停止播放")
        tts.stop_current_playback()
        
        # 发送新的请求
        new_text = "这是停止后的新音频。"
        new_request_id = tts.send_tts_request(new_text)
        print(f"新请求: {new_request_id}")
        
        tts.wait_for_completion()
        
    finally:
        tts.close()

def error_handling_example():
    """错误处理示例"""
    print("=== 错误处理示例 ===")
    
    try:
        # 使用无效的API配置
        tts = StreamingTTS()
        tts.set_api_config(api_key="invalid_key")
        
        # 尝试发送请求
        result = tts.send_tts_request("测试文本")
        if result is None:
            print("请求失败，可能是API配置错误")
        
        tts.close()
        
    except Exception as e:
        print(f"捕获异常: {e}")

def utility_functions_example():
    """工具函数示例"""
    print("=== 工具函数示例 ===")
    
    # 生成请求ID
    req_id = generate_request_id("demo")
    print(f"生成的请求ID: {req_id}")
    
    # 格式化时长
    duration = 125.5
    formatted = format_duration(duration)
    print(f"格式化时长: {formatted}")
    
    # 模拟音频数据保存
    dummy_audio = b"\x00" * 1000  # 模拟音频数据
    filename = "test_audio.wav"
    success = save_audio_to_file(dummy_audio, filename)
    print(f"保存音频文件: {'成功' if success else '失败'}")

if __name__ == "__main__":
    print("TTS包使用示例")
    print("=" * 50)
    
    # 运行示例
    try:
        basic_usage_example()
        print()
        
        advanced_usage_example()
        print()
        
        playback_control_example()
        print()
        
        error_handling_example()
        print()
        
        utility_functions_example()
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"运行示例时出错: {e}")
    
    print("\n示例运行完成")