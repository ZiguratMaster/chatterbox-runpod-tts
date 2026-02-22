FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Solo deps CRÍTICAS, sin requirements.txt
RUN pip install --no-cache-dir runpod
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
RUN pip install --no-cache-dir transformers==4.44.2 accelerate safetensors librosa soundfile pydub numpy scipy tqdm

# Chatterbox ÚLTIMO
RUN pip install --no-cache-dir git+https://github.com/resemble-ai/chatterbox.git

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]