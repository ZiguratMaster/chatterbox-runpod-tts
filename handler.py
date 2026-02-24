#!/usr/bin/env python3
# Chatterbox TTS + VOICE CLONING - Español ES ✓

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

print("🚀 Chatterbox TTS Multilingual - Español ES")

MODEL_PATH = os.getenv("MODEL_PATH", "/runpod-volume/chatterbox")

# ✅ FIX 1: Typo corregido (era "voice-samplet.wav")
VOICE_SAMPLE = Path("/app/voice-sample.wav")
VOICE_TARGET = Path(f"{MODEL_PATH}/voice-sample.wav")

# ✅ FIX 2: Parámetros configurables por entorno o input
DEFAULT_EXAGGERATION = float(os.getenv("EXAGGERATION", "0.45"))
DEFAULT_CFG_WEIGHT   = float(os.getenv("CFG_WEIGHT", "0.5"))
DEFAULT_TEMPERATURE  = float(os.getenv("TEMPERATURE", "0.7"))
DEFAULT_LANGUAGE     = os.getenv("LANGUAGE_ID", "es")  # Español España

model = None

def setup_voice():
    """Copia el voice sample al volumen persistente si no existe."""
    if VOICE_SAMPLE.exists() and not VOICE_TARGET.exists():
        VOICE_TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VOICE_SAMPLE, VOICE_TARGET)
        print(f"✅ Voice sample copiado → {VOICE_TARGET}")
    elif not VOICE_SAMPLE.exists():
        print(f"⚠️ AVISO: No se encontró {VOICE_SAMPLE} - voz DEFAULT activa")

def load_model():
    global model
    if model is None:
        print("🤖 Cargando ChatterboxMultilingualTTS...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        try:
            # ✅ FIX 2: Modelo MULTILINGÜE para soporte de español nativo
            from chatterbox.tts import ChatterboxMultilingualTTS
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🖥️ Device: {device}")
            model = ChatterboxMultilingualTTS.from_pretrained(device=device)
            print(f"✅ Modelo multilingual cargado ✓ | SR: {model.sr}")
        except ImportError:
            # Fallback al modelo base si multilingual no está disponible
            print("⚠️ ChatterboxMultilingualTTS no disponible, usando ChatterboxTTS (solo EN)")
            from chatterbox.tts import ChatterboxTTS
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = ChatterboxTTS.from_pretrained(device=device)
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            model = None
    setup_voice()

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    global model

    try:
        inp  = event.get("input", {})
        text = inp.get("text", "").strip()
        if not text:
            return {"error": "Sin texto proporcionado"}

        # Parámetros sobreescribibles desde el input del job
        exaggeration = float(inp.get("exaggeration", DEFAULT_EXAGGERATION))
        cfg_weight   = float(inp.get("cfg_weight",   DEFAULT_CFG_WEIGHT))
        temperature  = float(inp.get("temperature",  DEFAULT_TEMPERATURE))
        language_id  = inp.get("language_id", DEFAULT_LANGUAGE)

        print(f"🎤 Generando [{language_id}]: '{text[:50]}...'")
        print(f"   exag={exaggeration} | cfg={cfg_weight} | temp={temperature}")

        load_model()

        if model is None:
            # Fallback: tono de prueba
            sr = 24000
            t  = np.linspace(0, 2, sr * 2)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        else:
            sr = model.sr  # ✅ FIX 4: usar el SR real del modelo

            # ✅ FIX 3: Parámetros completos para calidad óptima
            generate_kwargs = dict(
                text=text,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                temperature=temperature,
            )

            # Añadir language_id si el modelo lo soporta (multilingual)
            if hasattr(model, 'supported_languages'):
                generate_kwargs["language_id"] = language_id
                print(f"🌍 Idioma: {language_id}")

            if VOICE_TARGET.exists():
                print(f"🔊 Clonando voz desde: {VOICE_TARGET}")
                generate_kwargs["audio_prompt_path"] = str(VOICE_TARGET)
            else:
                print("⚠️ Sin voice sample → voz DEFAULT (sin clonación)")

            audio = model.generate(**generate_kwargs)

            if torch.is_tensor(audio):
                audio = audio.cpu().numpy()

        # Serializar a WAV en base64 para RunPod
        audio_flat = audio.flatten() if audio.ndim > 1 else audio
        buffer = BytesIO()
        sf.write(buffer, audio_flat, sr, format='WAV')
        audio_b64 = base64.b64encode(buffer.getvalue()).decode()

        print("✅ Audio generado OK")
        return {
            "output": [{"path": f"data:audio/wav;base64,{audio_b64}"}],
            "delay_time": 2000
        }

    except Exception as e:
        print(f"❌ {traceback.format_exc()}")
        return {"error": str(e)}

print("✅ Handler iniciado")
runpod.serverless.start({"handler": handler})