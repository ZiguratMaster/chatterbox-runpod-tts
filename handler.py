# handler.py XTTS
import runpod
from TTS.api import TTS
import numpy as np
import io, wave

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

def handler(event):
    input_data = event["input"]
    if input_data.get("ping"):
        return {"status": "warm"}
    
    text = input_data["text"]
    speaker = "/vol/audio_ref_es.wav"
    
    wav = tts.tts(text=text, speaker_wav=speaker, language="es")
    audio_np = np.array(wav).astype(np.float32)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(24000)
        f.writeframes((audio_np * 32767).astype(np.int16).tobytes())
    
    return {"audio": buffer.getvalue().hex(), "format": "wav"}

runpod.serverless.start({"handler": handler})