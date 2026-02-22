# Dockerfile XTTS
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
RUN apt-get update && apt-get install -y ffmpeg espeak-ng && apt-get clean
RUN pip install --no-cache-dir TTS==0.22.0 torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu124
COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav
CMD ["python", "/handler.py"]