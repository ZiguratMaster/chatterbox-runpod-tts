FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && \
    apt-get install -y git ffmpeg espeak-ng python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124
RUN pip install TTS

RUN pip install runpod librosa soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]