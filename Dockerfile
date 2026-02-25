FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-dev python3-pip \
    build-essential pkg-config cmake \
    ffmpeg libsndfile1 git wget \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

WORKDIR /app

# torch PRIMERO con wheels
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

COPY . /app/

RUN python -m pip install --no-cache-dir \
    hf_transfer runpod soundfile librosa numpy requests pydantic huggingface_hub \
    && python -m pip install --no-cache-dir "chatterbox-tts@git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV PYTHONUNBUFFERED=1

EXPOSE 4123
CMD ["python", "-u", "handler.py"]