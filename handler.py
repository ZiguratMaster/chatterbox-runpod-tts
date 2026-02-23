import runpod
from TTS.api import TTS
import io
import numpy as np
import wave

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=True)

def handler(event):
    job_input = event['input']
    
    if job_input.get('ping'):
        return {'status': 'warm'}
    
    text = job_input['text']
    
    # XTTS clon
    out = tts.tts(text=text, speaker_wav="/vol/audio_ref_es.wav", language='es')
    
    # WAV
    audio_np = np.array(out).astype(np.float32)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes((audio_np * 32767).astype(np.int16).tobytes())
    
    return {'audio': buffer.getvalue().hex(), 'format': 'wav'}

runpod.serverless.start({'handler': handler})