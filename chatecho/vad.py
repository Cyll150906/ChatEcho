import webrtcvad
import struct

# VAD 参数设置
AUDIO_RATE = 16000        # 音频采样率
VAD_MODE = 3              # VAD 模式 (0-3, 数字越大越敏感)
VOLUME_THRESHOLD = 2000   # 音量阈值，低于此值认为是静音
VAD_CONFIDENCE_THRESHOLD = 0.1  # VAD置信度阈值

# 初始化 WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def get_audio_volume(audio_data):
    """计算音频数据的RMS音量"""
    # 将字节数据转换为16位整数
    if len(audio_data) == 0:
        return 0
    audio_ints = struct.unpack('<' + 'h' * (len(audio_data) // 2), audio_data)
    # 计算RMS
    if not audio_ints:
        return 0
    rms = (sum(x * x for x in audio_ints) / len(audio_ints)) ** 0.5
    return rms

def check_vad_activity(audio_data):
    """检测 VAD 活动（增强版）"""
    # 首先检查音量阈值
    volume = get_audio_volume(audio_data)
    if volume < VOLUME_THRESHOLD:
        return False
    
    # 将音频数据分块检测
    num, rate = 0, VAD_CONFIDENCE_THRESHOLD
    step = int(AUDIO_RATE * 0.02)  # 20ms 块大小
    if step == 0: # Avoid division by zero if audio_data is too short
        return False
    flag_rate = round(rate * len(audio_data) // step)

    for i in range(0, len(audio_data), step):
        chunk = audio_data[i:i + step]
        if len(chunk) == step:
            try:
                if vad.is_speech(chunk, sample_rate=AUDIO_RATE):
                    num += 1
            except: # webrtcvad can throw an error on invalid chunk size
                pass

    # 需要更高的置信度才认为是语音
    if num > flag_rate:
        return True
    return False