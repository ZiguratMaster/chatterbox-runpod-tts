import runpod
import torch
import torchaudio as ta
import base64
import os
import tempfile
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# Detectar dispositivo (GPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"--- Cargando modelo en {DEVICE}... ---")
try:
    # Carga el modelo multilingüe. La primera vez descargará ~1-2GB.
    model = ChatterboxMultilingualTTS.from_pretrained(device=DEVICE)
    print("--- Modelo cargado correctamente ---")
except Exception as e:
    print(f"--- Error cargando modelo: {e} ---")
    raise e

def handler(event):
    """
    Ejecuta la inferencia TTS.
    Input esperado (JSON):
    {
        "input": {
            "text": "Hola mundo",
            "language_id": "es",            (opcional, default: es)
            "audio_prompt_wav_b64": "...",  (opcional, base64 del wav)
            "cfg_weight": 0.5,              (opcional, fidelidad al audio)
            "exaggeration": 0.5             (opcional, expresividad)
        }
    }
    """
    job_input = event.get("input", event)

    # 1. Extraer parámetros
    text = job_input.get("text")
    if not text:
        return {"error": "No text provided"}

    language_id = job_input.get("language_id", "es")
    cfg_weight = float(job_input.get("cfg_weight", 0.5))
    exaggeration = float(job_input.get("exaggeration", 0.5))
    
    # 2. Gestionar el Audio Prompt (Voz a clonar)
    audio_prompt_path = None
    temp_audio_file = None

    # Caso A: Audio viene en base64 en la petición
    b64_audio = job_input.get("audio_prompt_wav_b64")
    if b64_audio:
        try:
            decoded = base64.b64decode(b64_audio)
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_audio_file.write(decoded)
            temp_audio_file.close()
            audio_prompt_path = temp_audio_file.name
        except Exception as e:
            return {"error": f"Invalid base64 audio: {str(e)}"}
    
    # Caso B: No hay base64, miramos si hay uno por defecto en el Docker
    elif os.getenv("DEFAULT_AUDIO_PROMPT") and os.path.exists(os.getenv("DEFAULT_AUDIO_PROMPT")):
        audio_prompt_path = os.getenv("DEFAULT_AUDIO_PROMPT")

    # 3. Generar Audio
    try:
        # Chatterbox devuelve un tensor
        wav = model.generate(
            text,
            language_id=language_id,
            audio_prompt_path=audio_prompt_path,
            cfg_weight=cfg_weight,
            exaggeration=exaggeration
        )
        
        # Guardar resultado a un fichero temporal para leerlo
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        output_file.close()
        
        # Asegurar dimensiones correctas (1, N)
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
            
        ta.save(output_file.name, wav, model.sr)

        # 4. Codificar a Base64 para devolverlo
        with open(output_file.name, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        # Limpieza del output
        os.unlink(output_file.name)

        return {
            "audio_wav_b64": audio_b64,
            "sample_rate": model.sr,
            "text": text
        }

    except Exception as e:
        return {"error": str(e)}
        
    finally:
        # Limpiar audio temporal de entrada si se creó
        if temp_audio_file and os.path.exists(temp_audio_file.name):
            os.unlink(temp_audio_file.name)

# Iniciar el worker
runpod.serverless.start({"handler": handler})