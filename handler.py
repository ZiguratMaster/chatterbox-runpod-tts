import runpod
from TTS.api import TTS
import numpy as np
import io
import wave

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

def handler(event):
    input_data = event["input"]
    if input_data.get("ping"):
        return {"status": "warm"}
    
    text = input_data["text"]
    speaker_wav = "/vol/audio_ref_es.wav"
    
    # Genera
    audio = tts.tts(text=text, speaker_wav=speaker_wav, language="es")
    
    # WAV bytes
    audio_np = np.array(audio).astype(np.float32)
    buffer = io.BytesIO()
    with wave.open(buffer
