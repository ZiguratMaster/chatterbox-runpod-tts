import runpod
import torch
import torchaudio as ta
import base64
import os
import tempfile
import traceback

try:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    CHATTERBOX_AVAILABLE = True
except ImportError:
    CHATTERBOX_AVAILABLE = False

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Usando dispositivo: {DEVICE}")

# Cargar modelo al inicio (solo la primera vez)
model = None
if CHATTERBOX_AVAILABLE:
    print("[INFO] Cargando modelo Chatterbox...")
    try:
        model = ChatterboxMultilingualTTS.from_pretrained(device=DEVICE)
        print("[INFO] ✅ Modelo Chatterbox cargado correctamente")
    except Exception as e:
        print(f"[ERROR] Fallo cargando Chatterbox: {e}")
        model = None

def handler(job):
    """
    Handler para Runpod Serverless
    """
    try:
        job_input = job.get("input", {})
        text = job_input.get("text", "Prueba de Chatterbox TTS")
        
        print(f"[INFO] Procesando: '{text[:50]}...'")
        
        if model is None:
            return {
                "output": "❌ Chatterbox no disponible. Usa texto simple.",
                "text": text,
                "device": DEVICE
            }
        
        # Audio prompt opcional
        audio_prompt_path = None
        temp_audio_file = None
        
        b64_audio = job_input.get("audio_prompt_wav_b64")
        if b64_audio:
            try:
                decoded = base64.b64decode(b64_audio)
                temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_audio_file.write(decoded)
                temp_audio_file.close()
                audio_prompt_path = temp_audio_file.name
                print("[INFO] Audio prompt cargado")
            except Exception as e:
                print(f"[WARNING] Error audio prompt: {e}")
        
        # Generar TTS
        language_id = job_input.get("language_id", "es")
        cfg_weight = float(job_input.get("cfg_weight", 0.5))
        exaggeration = float(job_input.get("exaggeration", 0.5))
        
        wav = model.generate(
            text,
            language_id=language_id,
            audio_prompt_path=audio_prompt_path,
            cfg_weight=cfg_weight,
            exaggeration=exaggeration
        )
        
        # Guardar WAV
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_file.close()
        
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        ta.save(output_file.name, wav, model.sr)
        
        # Base64 para respuesta
        with open(output_file.name, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        # Limpieza
        os.unlink(output_file.name)
        if temp_audio_file and os.path.exists(temp_audio_file.name):
            os.unlink(temp_audio_file.name)
        
        print("[INFO] ✅ Audio generado exitosamente")
        return {
            "audio_wav_b64": audio_b64,
            "sample_rate": model.sr,
            "text": text,
            "duration_seconds": len(wav[0]) / model.sr
        }
        
    except Exception as e:
        error_msg = f"Error TTS: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(traceback.format_exc())
        return {
            "error": error_msg,
            "text": text if 'text' in locals() else "Error",
            "device": DEVICE
        }

# ¡ESTA LÍNEA ES OBLIGATORIA para que el worker NO SALGA!
if __name__ == "__main__":
    print("[INFO] ✅ Iniciando Serverless Worker Chatterbox TTS")
    runpod.serverless.start({"handler": handler})