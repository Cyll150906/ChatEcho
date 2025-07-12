"""音频处理工具模块"""
import struct

def parse_wav_header(data):
    """解析WAV文件头，返回音频数据开始位置"""
    try:
        if len(data) < 44:  # WAV头至少44字节
            return None
        
        # 检查RIFF标识
        if data[:4] != b'RIFF':
            return None
        
        # 检查WAVE标识
        if data[8:12] != b'WAVE':
            return None
        
        # 查找data chunk
        pos = 12
        while pos < len(data) - 8:
            chunk_id = data[pos:pos+4]
            chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            
            if chunk_id == b'data':
                return pos + 8  # 返回音频数据开始位置
            
            pos += 8 + chunk_size
        
        return None
    except:
        return None