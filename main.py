from chatecho.recorder import Recorder
from chatecho.speech_processor import SpeechProcessor
from chatecho.sdk import VoiceToTextSDK
from chatecho.init import ChatWithHistory
import time

def main():
    sdk = VoiceToTextSDK()
    chat = ChatWithHistory()
    # You might want to load a system prompt for the chat here
    # with open('path/to/prompt.txt', 'r', encoding='utf-8') as file:
    #     text = file.read()
    # chat.set_system_prompt(text)

    processor = SpeechProcessor(sdk, chat)
    recorder = Recorder(processor)

    print("按 Enter 键开始录音，再次按 Enter 键停止录音。")
    input()
    recorder.start_recording()

    input()
    recorder.stop_recording()

if __name__ == "__main__":
    main()