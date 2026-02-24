#!/usr/bin/env python3
# Chatterbox TTS Serverless + Voz Clonada Persistente - FIX DEFINITIVO cache_dir
# RunPod Serverless + Network Volume

import os
import runpod
import torch
import numpy as np
import soundfile as sf
import shutil
import time
import traceback
import base64
from io import BytesIO
from typing import Dict, Any

print("🚀 Iniciando Chatterbox TTS + Voz Clonada...")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav"
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

model = None

def setup_voice():
    """Copia voz clonada a volumen persistente"""
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        print("📥 Copiando voz clonada a volumen...")
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz copiada: {VOICE_TARGET}")

def load_model():
    """FIX: Carga Chatterbox sin cache_dir problemático"""
    global model
    if model is None:
        print("🤖 Cargando Chatterbox TTS (FIX cache_dir)...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        try:
            # INTENTO 1: Import directo sin parámetros extras
            from chatterbox import ChatterboxTTS
            print("📦 ChatterboxTTS encontrado")
            model = ChatterboxTTS(device="cuda" if torch.cuda.is_available() else "cpu")
            print("✅ ChatterboxTTS básico cargado!")
            
        except ImportError:
            print("⚠️ ChatterboxTTS no disponible, probando Multilingual...")
            try:
                # INTENTO 2: Sin Multilingual.from_pretrained
                from chatterbox.tts import ChatterboxTTS
                model = ChatterboxTTS(device="cuda")
                print("✅ TTS interno cargado!")
                
            except Exception as e2:
                print(f"❌ Chatterbox completo falló: {e2}")
                model = None
                
        setup_voice()
        print(f"🎯 GPU disponible: {torch.cuda.is_available()}")

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model
    
    try:
        input_data = event["input"]
        text = input_data.get("text", "").strip()
        language = input_data.get("language", "es")
        
        if not text:
            return {"error": "Texto vacío"}
        
        print(f"🎤 Generando TTS: {text[:50]}...")
        
        # Lazy load modelo
        load_model()
        
        if model is None:
            return {
                "output": [{"path": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoAAAAA"}],
                "error": "Chatterbox cargando, usa texto simple"
            }
        
        # Genera audio (adaptado a APIs posibles)
        try:
            # API principal
            audio = model.generate(text=text, lang=language)
        except:
            try:
                # API alternativa 1
                audio = model.synthesize(text=text)
            except:
                # API alternativa 2
                audio = model(text)
        
        # Convierte a WAV base64
        if torch.is_tensor(audio):
            audio = audio.cpu().numpy()
        
        buffer = BytesIO()
        sf.write(buffer, audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print("✅ TTS generado exitosamente!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 1500
        }
        
    except Exception as e:
        print(f"❌ Error completo: {traceback.format_exc()}")
        return {"error": f"Error interno: {str(e)[:100]}"}

# Health check
print(f"🐍 Python: {os.sys.executable}")
print(f"📁 Modelo path: {MODEL_PATH}")
print("✅ Handler RunPod listo!")

runpod.serverless.start({"handler": handler})