FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Instala Python 3.11 + deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

WORKDIR /app
COPY . /app/

# Tu pip install (perfecto)
RUN python -m pip install --no-cache-dir \
    hf_transfer \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch torchaudio \
    runpod \
    soundfile librosa numpy requests pydantic \
    huggingface_hub \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV PYTHONUNBUFFERED=1

EXPOSE 4123
CMD ["python", "-u", "handler.py"]