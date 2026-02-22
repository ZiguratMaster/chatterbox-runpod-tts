import runpod
import torch
import torchaudio
from chatterbox.tts import ChatterboxTTS  # Multilingual
import numpy as np
import io
import wave

# Carga modelo al inicio (warm)
model = ChatterboxTTS.from_pretrained("mtl_tts")  # Multilingual para ES-ES
ref_path = "/vol/audio_ref_es.wav"
model.set_voice(ref_path)  # Clon voz

def handler(event):
    input_data = event["input"]
    if input_data.get("ping"):
        return {"status": "warm", "uptime": 1}
    
    text = input_data["text"]
    audio = model.generate(text, lang="es")  # Genera español
    
    # Convierte a WAV bytes
    audio_np = np.array(audio).astype(np.float32)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes((audio_np * 32767).astype(np.int16).tobytes())
    audio_bytes = buffer.getvalue()
    
    return {"audio": audio_bytes.hex(), "format": "wav"}  # Hex para JSON

runpod.serverless.start({"handler": handler})
