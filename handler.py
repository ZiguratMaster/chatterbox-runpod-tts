import runpod
import os
import time
import numpy as np
import io
import wave
from chatterbox import ChatterboxTTS

model = None

def load_model():
    global model
    if model is None:
        print("=== CARGANDO CHATTERBOX ===")
        model = ChatterboxTTS.from_pretrained("mtl_tts")
        print("=== CHATTERBOX LISTO ===")
    return model

def handler(event):
    print("=== HANDLER INICIADO ===")
    input_data = event["input"]
    
    if input_data.get("ping"):
        return {"status": "warm", "loaded": model is not None}
    
    text = input_data.get("text", "")
    print(f"TEXT: {text}")
    
    try:
        model = load_model()
        ref_audio = "/vol/audio_ref_es.wav"
        model.set_voice(ref_audio)
        audio = model.generate(text, lang="es")
        
        # Audio a WAV
        audio_np = np.array(audio).astype(np.float32)
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes((audio_np * 32767).astype(np.int16).tobytes())
        
        print("=== AUDIO GENERADO ===")
        return {"audio": buffer.getvalue().hex(), "format": "wav"}
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
print("=== SERVER READY ===")