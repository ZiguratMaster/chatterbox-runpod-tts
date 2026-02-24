#!/usr/bin/env python3
# Chatterbox TTS Serverless + Voz Clonada Persistente
# RunPod + Network Volume

import os
import runpod
import torch
import numpy as np
import soundfile as sf
import shutil
import time
import traceback
from typing import Optional, Dict, Any
from chatterbox import ChatterboxMultilingualTTS
import base64
from io import BytesIO

print("🚀 Iniciando Chatterbox TTS + Voz Clonada...")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav"
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

model = None
voice_embedding = None

def setup_voice():
    """Copia voz clonada a volumen persistente en primer inicio"""
    global voice_embedding
    
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        print("📥 Copiando voz clonada a volumen persistente...")
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz copiada: {VOICE_TARGET}")
    
    if os.path.exists(VOICE_TARGET) and voice_embedding is None:
        print("🔊 Cargando voice embedding...")
        # Carga embedding para clonación (ajusta según Chatterbox API)
        audio, sr = sf.read(VOICE_TARGET)
        voice_embedding = model.extract_voice_embedding(audio, sr) if hasattr(model, 'extract_voice_embedding') else audio
        print("✅ Voice embedding listo!")

def load_model():
    """Lazy load del modelo"""
    global model
    if model is None:
        print("🤖 Cargando Chatterbox Multilingual TTS...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        model = ChatterboxMultilingualTTS.from_pretrained(device="cuda", cache_dir=MODEL_PATH)
        print("✅ Modelo cargado!")
        setup_voice()

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model, voice_embedding
    
    try:
        input_data = event["input"]
        text = input_data.get("text", "")
        language = input_data.get("language", "es")  # Español por defecto
        
        if not text.strip():
            return {"error": "Texto vacío"}
        
        load_model()
        
        print(f"🎤 Generando TTS: {text[:50]}...")
        
        # Genera audio con voz clonada
        wav = model.generate(
            text=text,
            language_id=language,
            audio_prompt_path=VOICE_TARGET if voice_embedding else None
        )
        
        # Convierte a base64 para RunPod
        buffer = BytesIO()
        sf.write(buffer, wav.cpu().numpy(), model.sr, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print("✅ TTS generado!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 1500
        }
        
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc()}")
        return {"error": str(e)}

# RunPod Serverless entrypoint
runpod.serverless.start({"handler": handler})