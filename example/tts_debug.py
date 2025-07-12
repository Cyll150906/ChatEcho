"""TTS请求调试脚本
用于诊断TTS API请求和音频数据处理问题
"""
import requests
import os
import sys
import time
import struct
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts.env_config import get_secure_config, validate_api_key
from tts.audio_utils import parse_wav_header

def test_api_connection():
    """测试API连接"""
    print("=== API连接测试 ===")
    try:
        config = get_secure_config()
        print(f"✅ 配置加载成功")
        print(f"📡 API URL: {config.api.url}")
        print(f"🔑 API Key: {config.api.key[:27]}...")
        print(f"🎵 默认模型: {config.api.default_model}")
        print(f"🔊 默认声音: {config.api.default_voice}")
        
        # 验证API密钥
        if validate_api_key(config.api.key):
            print("✅ API密钥格式验证通过")
        else:
            print("❌ API密钥格式验证失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_api_request():
    """测试API请求"""
    print("\n=== API请求测试 ===")
    try:
        config = get_secure_config()
        
        # 准备请求数据
        payload = {
            "input": "这是一个测试。",
            "response_format": "wav",
            "sample_rate": 44100,
            "stream": True,
            "speed": 1.0,
            "gain": 0.0,
            "model": config.api.default_model,
            "voice": config.api.default_voice
        }
        
        headers = {
            "Authorization": config.api.key,
            "Content-Type": "application/json"
        }
        
        print(f"📤 发送请求到: {config.api.url}")
        print(f"📝 请求文本: {payload['input']}")
        print(f"🎵 使用模型: {payload['model']}")
        print(f"🔊 使用声音: {payload['voice']}")
        
        # 发送请求
        response = requests.post(config.api.url, json=payload, headers=headers, stream=True, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
        
        print("✅ API请求成功")
        return response
        
    except Exception as e:
        print(f"❌ API请求异常: {e}")
        return False

def test_audio_data_processing(response):
    """测试音频数据处理"""
    print("\n=== 音频数据处理测试 ===")
    try:
        audio_buffer = bytearray()
        wav_header_parsed = False
        chunk_count = 0
        total_bytes = 0
        
        print("📥 开始接收音频数据...")
        
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                chunk_count += 1
                total_bytes += len(chunk)
                audio_buffer.extend(chunk)
                
                print(f"📦 接收数据块 {chunk_count}: {len(chunk)} 字节 (总计: {total_bytes} 字节)")
                
                # 如果还没有解析WAV头
                if not wav_header_parsed and len(audio_buffer) >= 44:
                    print("🔍 尝试解析WAV头...")
                    
                    # 显示前44字节的十六进制内容
                    header_hex = ' '.join(f'{b:02x}' for b in audio_buffer[:44])
                    print(f"📋 WAV头数据 (前44字节): {header_hex}")
                    
                    # 检查RIFF标识
                    if audio_buffer[:4] == b'RIFF':
                        print("✅ 检测到RIFF标识")
                    else:
                        print(f"❌ 未检测到RIFF标识，实际: {audio_buffer[:4]}")
                    
                    # 检查WAVE标识
                    if audio_buffer[8:12] == b'WAVE':
                        print("✅ 检测到WAVE标识")
                    else:
                        print(f"❌ 未检测到WAVE标识，实际: {audio_buffer[8:12]}")
                    
                    data_start = parse_wav_header(audio_buffer)
                    if data_start is not None:
                        wav_header_parsed = True
                        print(f"✅ WAV头解析成功，音频数据开始位置: {data_start}")
                        
                        # 移除WAV头
                        audio_data = audio_buffer[data_start:]
                        print(f"🎵 音频数据长度: {len(audio_data)} 字节")
                        
                        # 保存音频数据到文件用于调试
                        with open('debug_audio.wav', 'wb') as f:
                            f.write(audio_buffer[:data_start])  # WAV头
                            f.write(audio_data)  # 音频数据
                        print("💾 音频数据已保存到 debug_audio.wav")
                        
                    else:
                        print("❌ WAV头解析失败")
                
                # 限制接收的数据量，避免测试时间过长
                if total_bytes > 50000:  # 50KB
                    print("⏹️ 达到测试数据量限制，停止接收")
                    break
        
        print(f"📊 数据接收完成: {chunk_count} 个数据块, 总计 {total_bytes} 字节")
        
        if wav_header_parsed:
            print("✅ 音频数据处理测试通过")
            return True
        else:
            print("❌ 音频数据处理测试失败：未能解析WAV头")
            return False
        
    except Exception as e:
        print(f"❌ 音频数据处理异常: {e}")
        return False

def test_manual_audio_playback():
    """测试手动音频播放"""
    print("\n=== 手动音频播放测试 ===")
    try:
        # 检查是否有调试音频文件
        if not os.path.exists('debug_audio.wav'):
            print("❌ 未找到调试音频文件")
            return False
        
        import pyaudio
        import wave
        
        # 打开WAV文件
        with wave.open('debug_audio.wav', 'rb') as wf:
            print(f"🎵 音频文件信息:")
            print(f"   采样率: {wf.getframerate()} Hz")
            print(f"   通道数: {wf.getnchannels()}")
            print(f"   采样宽度: {wf.getsampwidth()} 字节")
            print(f"   帧数: {wf.getnframes()}")
            print(f"   持续时间: {wf.getnframes() / wf.getframerate():.2f} 秒")
            
            # 初始化PyAudio
            p = pyaudio.PyAudio()
            
            # 打开音频流
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            print("🔊 开始播放调试音频文件...")
            
            # 播放音频
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)
            
            print("✅ 调试音频播放完成")
            
            # 清理资源
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ 手动音频播放失败: {e}")
        return False

def main():
    """主调试函数"""
    print("🔧 TTS请求调试工具")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    tests = [
        ("API连接", test_api_connection),
        ("API请求", test_api_request),
    ]
    
    response = None
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 运行测试: {test_name}")
            result = test_func()
            if isinstance(result, requests.Response):
                response = result
                print(f"✅ {test_name} 测试通过")
            elif result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
                return
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断测试")
            return
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            return
    
    # 如果有响应，测试音频数据处理
    if response:
        if test_audio_data_processing(response):
            # 测试手动播放
            test_manual_audio_playback()
    
    print("\n" + "=" * 50)
    print("🎯 调试完成")
    print("\n💡 如果音频文件能正常播放但TTS系统无声音，问题可能在于:")
    print("   1. 音频数据流处理的时序问题")
    print("   2. 音频播放器的线程同步问题")
    print("   3. 音频数据块大小不匹配")
    print("   4. WAV头解析后的数据格式问题")

if __name__ == "__main__":
    main()