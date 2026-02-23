FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng git python3-dev gcc g++ make && apt-get clean

RUN pip install --upgrade pip setuptools wheel

RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# TTS con deps Rust
RUN pip install --no-cache-dir espeak-ng==0.1.10
RUN pip install --no-cache-dir TTS

RUN pip install --no-cache-dir runpod librosa soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]