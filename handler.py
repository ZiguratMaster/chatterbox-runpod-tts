import runpod
import time

def handler(event):
    print("=== HANDLER INICIADO ===")
    input_data = event["input"]
    
    if input_data.get("ping"):
        return {"status": "warm", "timestamp": time.time()}
    
    text = input_data.get("text", "No text")
    print(f"TTS request: {text}")
    
    # Simula TTS (devuelve dummy audio)
    audio_dummy = [0.0] * 48000  # 2s silencio 24kHz
    print("=== TTS SIMULADO OK ===")
    return {"audio": [float(x) for x in audio_dummy], "format": "wav", "text": text}

runpod.serverless.start({"handler": handler})
print("=== SERVERLESS STARTED ===")
