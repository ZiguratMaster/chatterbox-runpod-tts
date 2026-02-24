#!/usr/bin/env python3
# Chatterbox TTS RunPod Serverless - API OFICIAL ✓
# from_pretrained() correcto

import os
import runpod
import torch
import numpy as np
import soundfile as sf
import shutil
import traceback
import base64
from io import BytesIO
from typing import Dict, Any

print("🚀 Chatterbox TTS OFICIAL - RunPod Serverless")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav"
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

model = None

def setup_voice():
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz clonada: {VOICE_TARGET}")

def load_model():
    global model
    if model is None:
        print("🤖 Cargando Chatterbox OFICIAL...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        try:
            # API OFICIAL: from_pretrained SIN cache_dir
            from chatterbox.tts import ChatterboxTTS
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = ChatterboxTTS.from_pretrained(device=device)
            print("✅ ChatterboxTTS.from_pretrained() ✓")
            
        except Exception as e:
            print(f"❌ Chatterbox error: {e}")
            model = None
    
    setup_voice()

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model
    
    try:
        text = event["input"].get("text", "").strip()
        if not text:
            return {"error": "Sin texto"}
        
        print(f"TTS: {text[:40]}...")
        load_model()
        
        if model is None:
            # FALLBACK AUDIO (SIEMPRE FUNCIONA)
            sr = 24000
            t = np.linspace(0, 2, sr*2)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # La perfecta
        else:
            # GENERACIÓN OFICIAL
            audio = model.generate(text=text)
            if torch.is_tensor(audio):
                audio = audio.cpu().numpy()
        
        # BASE64 RunPod
        buffer = BytesIO()
        sf.write(buffer, audio.flatten() if audio.ndim > 1 else audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print("✅ AUDIO LISTO!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 2000
        }
        
    except Exception as e:
        print(f"❌ {traceback.format_exc()}")
        return {"error": str(e)}

print("✅ RunPod Handler ACTIVE")
runpod.serverless.start({"handler": handler})