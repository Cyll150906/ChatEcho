import os
import time
import wave
import threading
from .sdk import VoiceToTextSDK
from .init import ChatWithHistory

OUTPUT_DIR = "./temp_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SpeechProcessor:
    def __init__(self, sdk: VoiceToTextSDK, chat: ChatWithHistory):
        self.sdk = sdk
        self.chat = chat
        self.audio_file_count = 0
        self.tts_was_interrupted = False

    def process_speech(self, audio_path, interrupted):
        print(f"🎤 开始处理语音: {audio_path}")
        try:
            recognized_text = self.sdk.transcribe_audio(audio_path)
            print(f'📝 识别结果: "{recognized_text}" (打断状态: {interrupted})')

            if recognized_text:
                if interrupted:
                    print("🔴 TTS被打断，仅记录文本，不生成回复")
                else:
                    print("🤖 正在生成回复...")
                    response_text = self.chat.get_response(recognized_text)
                    print(f"💬 回复内容: {response_text}")
                    # 在这里添加TTS播放逻辑
            else:
                print("🤷‍♀️ 未识别到有效文本")
        except Exception as e:
            print(f"❌ 处理语音时出错: {e}")
        finally:
            try:
                os.remove(audio_path)
            except:
                pass

    def extract_and_process_speech_segment(self, continuous_audio_buffer, start_time, end_time, recording_start_time, pre_post_buffer_seconds):
        extract_start = max(start_time - pre_post_buffer_seconds, recording_start_time)
        extract_end = end_time + pre_post_buffer_seconds

        print(f"📁 截取音频片段: {extract_start:.2f} - {extract_end:.2f} (原语音: {start_time:.2f} - {end_time:.2f})")

        extracted_audio = [audio_data for audio_data, timestamp in continuous_audio_buffer if extract_start <= timestamp <= extract_end]

        if not extracted_audio:
            print("❌ 未找到对应时间段的音频数据")
            return

        self.audio_file_count += 1
        audio_output_path = f"{OUTPUT_DIR}/speech_{time.strftime('%Y%m%d_%H%M%S')}_{self.audio_file_count:03d}.wav"

        try:
            with wave.open(audio_output_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(b''.join(extracted_audio))
            print(f"💾 音频片段保存至 {audio_output_path}")

            current_interruption_status = self.tts_was_interrupted
            inference_thread = threading.Thread(target=self.process_speech, args=(audio_output_path, current_interruption_status))
            inference_thread.start()
            self.tts_was_interrupted = False
        except Exception as e:
            print(f"❌ 保存或处理音频时出错: {e}")