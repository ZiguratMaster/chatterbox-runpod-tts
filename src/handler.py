import runpod
import requests
import json

API_URL = "http://127.0.0.1:4123/v1/audio/speech"

def handler(job):
    input_data = job["input"]
    
    response = requests.post(API_URL, json={
        "model": "tts-1",
        "input": input_data["text"],
        "voice": "alloy",  # o tu voz clonada
        "response_format": "wav"
    })
    
    if response.status_code == 200:
        return {"audio": response.content}
    else:
        return {"error": response.text}

runpod.serverless.start({"handler": handler})