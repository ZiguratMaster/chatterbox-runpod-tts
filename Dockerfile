FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng build-essential && apt-get clean

# PyTorch CUDA primero (base)
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# TTS desde git (evita pip wheels rotos)
RUN pip install --no-cache-dir git+https://github.com/coqui-ai/TTS.git@master

RUN pip install --no-cache-dir runpod librosa soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]