#!/usr/bin/env python3
import os, sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from asr import StreamingASR

AUDIO_FILE = r"D:\PythonProject\AG\temp_audio\recording_20250710_182508.wav"

if not os.path.exists(AUDIO_FILE):
    sys.exit(f"❌ File not found: {AUDIO_FILE}")

print(f"🎤 Transcribing {os.path.basename(AUDIO_FILE)}...")
try:
    with StreamingASR.from_env() as asr:
        print(f"✅ Result: {asr.transcribe_file(AUDIO_FILE)}")
except Exception as e:
    sys.exit(f"❌ Error: {e}")