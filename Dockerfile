FROM python:3.11-slim

# Instala CUDA runtime mínimo (no devel/full)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instala CUDA 12.2 runtime
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
    && dpkg -i cuda-keyring_1.1-1_all.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends cuda-runtime-12-2 \
    && rm -rf /var/lib/apt/lists/* cuda-keyring_1.1-1_all.deb

WORKDIR /app
COPY . /app/

# Tu pip install exacto (está bien)
RUN python3.11 -m pip install --no-cache-dir \
    hf_transfer \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch torchaudio \
    runpod \
    soundfile librosa numpy requests pydantic \
    huggingface_hub \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV CUDA_VISIBLE_DEVICES=all

EXPOSE 4123
CMD ["python3.11", "-u", "handler.py"]