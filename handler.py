import runpod
from TTS.api import TTS
import numpy as np
import io
import wave
import re

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

def parse_emotion(text):
    if "risa" in text.lower():
        return text + " ja ja ja :)", 1.0  # Alegre
    elif "susurro" in text.lower():
        return "[bajo] " + text + " [bajo]", 0.3  # Temperature bajo
    return text, 0.7

def handler(event):
    input_data = event["input"]
    if input_data.get("ping"):
        return {"status": "warm"}
    
    text = input_data["text"]
    text, temp = parse_emotion(text)
    
    wav = tts.tts(text=text, speaker_wav="/vol/audio_ref_es.wav", 
                  language="es", temperature=temp)
    
    audio_np = np.array(wav).astype(np.float32)
    buffer = io.BytesIO()
    with wave.open(buffer
