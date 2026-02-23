FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg espeak-ng git python3-dev && apt-get clean

RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu124

# TTS precompiled (no git)
RUN pip install --no-cache-dir TTS==0.22.0 --no-build-isolation

RUN pip install --no-cache-dir runpod librosa==0.10.1 soundfile pydub numpy

COPY handler.py /handler.py
COPY audio_ref_es.wav /vol/audio_ref_es.wav

CMD ["python", "/handler.py"]