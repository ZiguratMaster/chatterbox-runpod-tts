FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Torch compatible CUDA 12.2 primero
RUN pip install --no-cache-dir \
    torch torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY . /app

# FIX: Instala hf_transfer + deps
RUN pip install --no-cache-dir \
    hf_transfer \
    runpod \
    soundfile librosa numpy requests pydantic \
    "huggingface_hub[hf_transfer]" \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

# Deshabilita solo si no quieres hf_transfer (pero mejor usarlo para velocidad)
ENV HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 4123

CMD ["python", "handler.py"]