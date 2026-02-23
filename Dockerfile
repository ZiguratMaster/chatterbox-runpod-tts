FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update -qq && apt-get install -y -qq ffmpeg espeak-ng git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# TTS precompiled (no git compile)
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir TTS==0.22.0

RUN pip install --no-cache-dir runpod librosa soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]