"""音频播放测试脚本
用于诊断音频播放问题
"""
import pyaudio
import numpy as np
import time
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pyaudio_installation():
    """测试PyAudio安装"""
    print("=== PyAudio 安装测试 ===")
    try:
        import pyaudio
        print("✅ PyAudio 导入成功")
        
        # 获取PyAudio版本
        p = pyaudio.PyAudio()
        print(f"✅ PyAudio 版本: {pyaudio.__version__}")
        
        # 获取音频设备信息
        device_count = p.get_device_count()
        print(f"✅ 检测到 {device_count} 个音频设备")
        
        # 列出所有音频设备
        print("\n📱 音频设备列表:")
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            print(f"  设备 {i}: {device_info['name']} (输出通道: {device_info['maxOutputChannels']})")
        
        # 获取默认输出设备
        default_output = p.get_default_output_device_info()
        print(f"\n🔊 默认输出设备: {default_output['name']}")
        print(f"   最大输出通道: {default_output['maxOutputChannels']}")
        print(f"   默认采样率: {default_output['defaultSampleRate']}")
        
        p.terminate()
        return True
        
    except Exception as e:
        print(f"❌ PyAudio 测试失败: {e}")
        return False

def test_audio_playback():
    """测试音频播放功能"""
    print("\n=== 音频播放测试 ===")
    try:
        # 生成测试音频（440Hz正弦波，持续1秒）
        sample_rate = 44100
        duration = 1.0  # 秒
        frequency = 440  # Hz (A4音符)
        
        # 生成正弦波
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # 转换为16位整数
        audio_data = (wave * 32767).astype(np.int16)
        
        print(f"🎵 生成测试音频: {frequency}Hz, {duration}秒, {sample_rate}Hz采样率")
        
        # 初始化PyAudio
        p = pyaudio.PyAudio()
        
        # 打开音频流
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True,
            frames_per_buffer=1024
        )
        
        print("🔊 开始播放测试音频...")
        
        # 播放音频
        chunk_size = 1024
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            stream.write(chunk.tobytes())
        
        print("✅ 测试音频播放完成")
        
        # 清理资源
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ 音频播放测试失败: {e}")
        return False

def test_tts_audio_player():
    """测试TTS音频播放器"""
    print("\n=== TTS 音频播放器测试 ===")
    try:
        from tts.player import AudioPlayer
        
        # 创建音频播放器
        player = AudioPlayer()
        print("✅ TTS音频播放器创建成功")
        
        # 生成测试音频数据
        sample_rate = 44100
        duration = 0.5
        frequency = 880  # Hz
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        audio_data = (wave * 32767).astype(np.int16)
        
        print(f"🎵 添加测试音频到播放队列: {frequency}Hz, {duration}秒")
        
        # 分块添加到播放器
        chunk_size = 2048
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            player.add_audio_chunk(chunk.tobytes())
        
        print("🔊 等待播放完成...")
        player.wait_for_completion()
        print("✅ TTS音频播放器测试完成")
        
        # 清理资源
        player.close()
        return True
        
    except Exception as e:
        print(f"❌ TTS音频播放器测试失败: {e}")
        return False

def test_system_audio():
    """测试系统音频设置"""
    print("\n=== 系统音频设置检查 ===")
    
    # 检查系统音量
    try:
        import platform
        system = platform.system()
        print(f"🖥️ 操作系统: {system}")
        
        if system == "Windows":
            print("💡 Windows系统音频检查提示:")
            print("   1. 检查系统音量是否静音")
            print("   2. 检查默认播放设备是否正确")
            print("   3. 检查应用程序音量混合器")
            print("   4. 尝试播放其他音频文件确认音频设备正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统音频检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 音频播放诊断工具")
    print("=" * 50)
    
    tests = [
        ("PyAudio安装", test_pyaudio_installation),
        ("系统音频设置", test_system_audio),
        ("基础音频播放", test_audio_playback),
        ("TTS音频播放器", test_tts_audio_player)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 运行测试: {test_name}")
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断测试")
            break
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总计: {passed}/{len(results)} 个测试通过")
    
    if passed < len(results):
        print("\n💡 故障排除建议:")
        print("   1. 确保系统音频设备正常工作")
        print("   2. 检查Python环境中PyAudio的安装")
        print("   3. 尝试重启音频服务或重新插拔音频设备")
        print("   4. 检查防火墙或安全软件是否阻止音频播放")

if __name__ == "__main__":
    main()