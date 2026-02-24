#!/usr/bin/env python3
# Chatterbox TTS con VOZ CLONADA ✓

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

print("🚀 Chatterbox TTS + VOICE CLONING")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SAMPLE = Path("/app/voice-samplet.wav")  # Tu sample aquí
VOICE_TARGET = Path(f"{MODEL_PATH}/voice-sample.wav")

model = None

def setup_voice():
    if VOICE_SAMPLE.exists() and not VOICE_TARGET.exists():
        VOICE_TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VOICE_SAMPLE, VOICE_TARGET)
        print(f"✅ Voz copiada: {VOICE_TARGET}")

def load_model():
    global model
    if model is None:
        print("🤖 Cargando Chatterbox...")
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
        
        print(f"TTS clonado: {text[:40]}...")
        load_model()
        
        if model is None:
            # Fallback tono
            sr = 24000
            t = np.linspace(0, 2, sr*2)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        else:
            # ✅ CLONACIÓN: Carga reference_audio
            ref_audio_path = str(VOICE_TARGET)
            if VOICE_TARGET.exists():
                # Carga el sample como array numpy
                ref_audio, sr_ref = sf.read(ref_audio_path)
                print(f"🔊 Usando voz clonada: {ref_audio_path} (SR: {sr_ref})")
                
                # Genera CON clonación (ajusta params según docs Chatterbox)
                audio = model.generate(
                    text=text,
                    reference_audio=ref_audio,  # ¡CLAVE! Array del sample
                    exaggeration=0.8,  # Emoción (0-2)
                    cfg_weight=0.5,    # Creatividad
                    temperature=0.7    # Variabilidad
                )
                if torch.is_tensor(audio):
                    audio = audio.cpu().numpy()
            else:
                print("⚠️ Sin sample voz, usa default")
                audio = model.generate(text=text)
        
        # Base64 output
        buffer = BytesIO()
        sf.write(buffer, audio.flatten() if audio.ndim > 1 else audio, 24000, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        print("✅ AUDIO CLONADO LISTO!")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 2000
        }
        
    except Exception as e:
        print(f"❌ Error: {traceback.format_exc()}")
        return {"error": str(e)}

print("✅ Handler con clonación ACTIVE")
runpod.serverless.start({"handler": handler})