import os

class Config:
    # API Configuration
    SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "sk-oyxoqrxbymcizdfmfuzdxtudualgftadigummmozhhpdjamu")
    SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
    API_TIMEOUT = 30

    # Model Names
    CHAT_MODEL = "Qwen/Qwen3-30B-A3B"
    ASR_MODEL = "Qwen/Qwen3-30B-A3B"  # Replace with actual ASR model if different
    TTS_MODEL = "FunAudioLLM/CosyVoice2-0.5B"
    TTS_VOICE = "FunAudioLLM/CosyVoice2-0.5B:anna"

    # Audio Configuration
    AUDIO_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_CHUNK = 1024
    TTS_SAMPLE_RATE = 44100

    # Directories
    TEMP_DIR = "./temp_audio"

    @staticmethod
    def get_api_key():
        return Config.SILICONFLOW_API_KEY

    @staticmethod
    def get_api_url(endpoint):
        return f"{Config.SILICONFLOW_BASE_URL}/{endpoint}"

    @staticmethod
    def get_temp_dir():
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        return Config.TEMP_DIR