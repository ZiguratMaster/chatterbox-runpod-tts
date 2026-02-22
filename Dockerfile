FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Fix deps CRÍTICO
RUN pip install --no-cache-dir torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124
RUN pip install --no-cache-dir transformers==4.44.0 accelerate safetensors

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]