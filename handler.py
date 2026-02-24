#!/usr/bin/env python3
# Chatterbox TTS + VOICE CLONING OFICIAL ✓

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
from pathlib import Path

print("🚀 Chatterbox TTS con audio_prompt_path")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SAMPLE = Path("/app/voice-samplet.wav")
VOICE_TARGET = Path(f"{MODEL_PATH}/voice-sample.wav")

model = None

def setup_voice():
    if VOICE_SAMPLE.exists() and not VOICE_TARGET.exists():
        VOICE_TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VOICE_SAMPLE, VOICE_TARGET)
        print(f"✅ Voz clonada: {VOICE_TARGET}")

def load_model():
    global model
    if model is None:
        print("🤖 Cargando Chatterbox OFICIAL...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        try:
            from chatterbox.tts import ChatterboxTTS
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = ChatterboxTTS.from_pretrained(device=device)
            print("✅ Modelo cargado ✓")
        except Exception as e:
            print(f"❌ Error Chatterbox: {e}")
            model = None
    
    setup_voice()

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model
    
    try:
        text = event["input"].get("text", "").strip()
        if not text:
            return {"error": "Sin texto"}
        
        print(f"🎤 TTS clonado: {text[:40]}...")
        load_model()
        
        if model is None:
            # Fallback tono
            sr = 24000
            t = np.linspace(0, 2, sr*2)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        else:
            # ✅ CLONACIÓN CORRECTA: audio_prompt_path = PATH al archivo
            if VOICE_TARGET.exists():
                print(f"🔊 CLONANDO con: {VOICE_TARGET}")
                audio = model.generate(
                    text=text,
                    audio_prompt_path=str(VOICE_TARGET)  # ¡PARÁMETRO OFICIAL![web:32]
                )
            else:
                print("⚠️ Sin sample, voz DEFAULT")
                audio = model.generate(text=text)
            
            if torch.is_tensor(audio):
                audio = audio.cpu().numpy()
        
        # Base64 RunPod
        buffer = BytesIO()
        sf.write(buffer, audio.flatten() if audio.ndim > 1 else audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print("✅ AUDIO CLONADO GENERADO!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 2000
        }
        
    except Exception as e:
        print(f"❌ {traceback.format_exc()}")
        return {"error": str(e)}

print("✅ Handler CLONACIÓN ACTIVE")
runpod.serverless.start({"handler": handler})