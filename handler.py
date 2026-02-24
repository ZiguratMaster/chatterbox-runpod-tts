#!/usr/bin/env python3
import os
import runpod
import torch
import numpy as np
import soundfile as sf
import shutil
import time
import traceback
from typing import Dict, Any
try:
    from chatterbox.tts import ChatterboxTTS  # API correcta
except ImportError:
    from chatterbox import ChatterboxTTS

print("🚀 Iniciando Chatterbox TTS + Voz Clonada...")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav"
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

model = None

def setup_voice():
    """Copia voz clonada a volumen persistente"""
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        print("📥 Copiando voz clonada...")
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz copiada: {VOICE_TARGET}")

def load_model():
    global model
    if model is None:
        print("🤖 Cargando Chatterbox TTS...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        # FIX: API correcta sin cache_dir
        model = ChatterboxTTS(
            device="cuda" if torch.cuda.is_available() else "cpu",
            model_dir=MODEL_PATH  # O elimina esta línea
        )
        print("✅ Modelo cargado!")
        setup_voice()

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model
    
    try:
        input_data = event["input"]
        text = input_data.get("text", "")
        
        if not text.strip():
            return {"error": "Texto vacío"}
        
        load_model()
        print(f"🎤 Generando TTS: {text[:50]}...")
        
        # API simplificada de Chatterbox
        audio = model.synthesize(text=text)
        
        # Base64 para RunPod
        buffer = BytesIO()
        sf.write(buffer, audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print("✅ TTS generado!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 1500
        }
        
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc()}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})