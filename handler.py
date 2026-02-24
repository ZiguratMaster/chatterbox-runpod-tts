import os
import runpod
import torch
import numpy as np
import soundfile as sf
import shutil
from chatterbox import ChatterboxMultilingualTTS

# Paths
MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")
VOICE_SOURCE = "/app/voice-samplet.wav"  # Desde GitHub build
VOICE_TARGET = f"{MODEL_PATH}/voice-sample.wav"

# Globales
model = None
voice_embedding = None

def setup_voice():
    """Copia voz de GitHub → Volumen persistente (solo primera vez)"""
    global voice_embedding
    
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH, exist_ok=True)
        print("📁 Creando directorio volumen...")
    
    # Copia voz si existe en container pero no en volumen
    if os.path.exists(VOICE_SOURCE) and not os.path.exists(VOICE_TARGET):
        print("📥 Copiando voice-samplet.wav → volumen persistente...")
        os.makedirs(os.path.dirname(VOICE_TARGET), exist_ok=True)
        shutil.copy2(VOICE_SOURCE, VOICE_TARGET)
        print(f"✅ Voz clonada guardada: {VOICE_TARGET}")
    
    # Carga embedding
    if os.path.exists(VOICE_TARGET):
        audio, sr = sf.read(VOICE_TARGET)
        if sr != 22050:
            from librosa import resample
            audio = resample(audio, int(len(audio) * 22050 / sr))
        voice_embedding = model.extract_voice_embedding(torch.tensor(audio).float().unsqueeze(0))
        print(f"✅ Voice embedding listo: {voice_embedding.shape}")
    else:
        print("⚠️  voice-sample.wav NO encontrado, usando voz default")
        voice_embedding = None

def load_model():
    """Carga modelo desde volumen"""
    global model
    print(f"🔍 Buscando modelo en: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH):
        print("✅ Cargando Chatterbox desde volumen...")
        model = ChatterboxMultilingualTTS.from_pretrained(MODEL_PATH, device="cuda")
        print("✅ Modelo listo en GPU!")
        setup_voice()  # Configura voz clonada
    else:
        print("❌ Volumen NO montado. Attach chatterbox-models volume.")
        model = None

def handler(event):
    global model, voice_embedding
    
    # Lazy load
    if model is None:
        load_model()
    
    if model is None:
        return {
            "output": {
                "error": "Modelo no disponible. Verifica volumen mount.",
                "check_volume": MODEL_PATH,
                "status": "error"
            }
        }
    
    # Input usuario
    input_data = event.get("input", {})
    text = input_data.get("text", "¡Hola mundo desde mi voz clonada!")
    
    print(f"🎤 Generando TTS: '{text[:50]}...'")
    
    # TTS con TU VOZ 👇
    try:
        if voice_embedding is not None:
            audio = model.generate(text, voice_embedding=voice_embedding)
            voice_used = "TU VOZ CLONADA 👤"
        else:
            audio = model.generate(text)
            voice_used = "default"
        
        print(f"✅ {voice_used} - {len(audio)} samples @ 22kHz")
        
        return {
            "output": {
                "audio": audio.tolist(),
                "sample_rate": 22050,
                "voice_used": voice_used,
                "text": text,
                "status": "success"
            }
        }
    except Exception as e:
        print(f"❌ Error TTS: {e}")
        return {"output": {"error": str(e), "status": "error"}}

# RunPod Serverless
if __name__ == "__main__":
    print("🚀 Chatterbox TTS + Voz Clonada iniciado!")
    runpod.serverless.start({"handler": handler})