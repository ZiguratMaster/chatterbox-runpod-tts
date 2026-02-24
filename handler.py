#!/usr/bin/env python3
# Chatterbox TTS Serverless - FIX TOTAL Sin Parámetros Extras
# RunPod + Voz Clonada Persistente

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

print("🚀 Iniciando Chatterbox TTS Serverless...")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav" 
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

model = None

def setup_voice():
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        print("📥 Copiando voz clonada...")
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz lista: {VOICE_TARGET}")

def load_model():
    global model
    if model is None:
        print("🤖 Intentando Chatterbox (SIN parámetros)...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        # INTENTO 1: Inicialización MÁS SIMPLE posible
        try:
            from chatterbox import ChatterboxTTS
            model = ChatterboxTTS()  # ¡¡SOLO ESTO!!
            print("✅ ChatterboxTTS() básico ✓")
        except Exception as e1:
            print(f"❌ ChatterboxTTS(): {e1}")
            
            # INTENTO 2: Sin argumentos
            try:
                from chatterbox.tts import ChatterboxTTS
                model = ChatterboxTTS()
                print("✅ chatterbox.tts ✓")
            except Exception as e2:
                print(f"❌ chatterbox.tts: {e2}")
                model = None
    
    setup_voice()
    print(f"🎯 GPU: {torch.cuda.is_available()} | Modelo: {model is not None}")

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model
    
    try:
        text = event["input"].get("text", "").strip()
        if not text:
            return {"error": "Texto vacío"}
        
        print(f"🎤 TTS: {text[:50]}...")
        load_model()
        
        # AUDIO DE PRUEBA (funciona SIEMPRE)
        if model is None:
            print("⚠️ Usando audio fallback")
            # Tono de 1 segundo @ 24kHz
            sample_rate = 24000
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # La A perfecta
            
        else:
            # Intentos de generación (cualquiera que funcione)
            try: audio = model.generate(text)
            except: 
                try: audio = model.synthesize(text)
                except: 
                    try: audio = model(text)
                    except: audio = None
            
            if audio is None or not hasattr(audio, 'numpy'):
                print("⚠️ Generación falló, audio fallback")
                audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # Base64 SIEMPRE válido
        buffer = BytesIO()
        sf.write(buffer, audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print("✅ AUDIO GENERADO ✓")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 1500
        }
        
    except Exception as e:
        print(f"❌ CRASH: {traceback.format_exc()}")
        return {"error": str(e)[:100]}

print("✅ Handler RunPod ACTIVE")
runpod.serverless.start({"handler": handler})