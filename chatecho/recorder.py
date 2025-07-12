import pyaudio
import time
import threading
from queue import Queue
from .audio_config import AUDIO_RATE, AUDIO_CHANNELS, CHUNK_SIZE, AUDIO_FORMAT
from .vad import check_vad_activity

class Recorder:
    def __init__(self, speech_processor):
        self.speech_processor = speech_processor
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.continuous_audio_buffer = []
        self.speech_segments = []
        self.recording_start_time = None
        self.last_speech_time = None
        self.silence_start_time = None

    def start_recording(self):
        self.is_recording = True
        self.recording_start_time = time.time()
        self.stream = self.p.open(format=AUDIO_FORMAT,
                                     channels=AUDIO_CHANNELS,
                                     rate=AUDIO_RATE,
                                     input=True,
                                     frames_per_buffer=CHUNK_SIZE)
        print("🎤 开始录音...")
        thread = threading.Thread(target=self.record_and_detect)
        thread.start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        print("🛑 录音结束.")

    def record_and_detect(self):
        while self.is_recording:
            try:
                audio_data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                current_time = time.time()
                self.continuous_audio_buffer.append((audio_data, current_time))

                is_speech = check_vad_activity(audio_data)

                if is_speech:
                    self.last_speech_time = current_time
                    if self.silence_start_time:
                        self.silence_start_time = None
                    if not self.speech_segments or self.speech_segments[-1][1] is not None:
                        self.speech_segments.append([current_time, None])
                else:
                    if self.last_speech_time and not self.silence_start_time:
                        self.silence_start_time = current_time

                    if self.silence_start_time and (current_time - self.silence_start_time > 2.0):
                        if self.speech_segments and self.speech_segments[-1][1] is None:
                            self.speech_segments[-1][1] = self.last_speech_time
                            start, end = self.speech_segments[-1]
                            self.speech_processor.extract_and_process_speech_segment(
                                self.continuous_audio_buffer, start, end, self.recording_start_time, 1.0
                            )
                        self.silence_start_time = None # Reset silence timer

                # Clean up old buffer data
                buffer_duration = 10 # seconds
                if self.recording_start_time:
                    cutoff_time = current_time - buffer_duration
                    self.continuous_audio_buffer = [(data, ts) for data, ts in self.continuous_audio_buffer if ts > cutoff_time]

            except IOError as e:
                print(f"录音错误: {e}")
                time.sleep(0.1)