FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Torch + hf_transfer primero
RUN pip install --no-cache-dir hf_transfer \
    torch torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY . /app/

# Instala todo con python3.11 explícito
RUN python3.11 -m pip install --no-cache-dir \
    runpod \
    soundfile librosa numpy requests pydantic \
    huggingface_hub \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 4123

# FIX: Usa python3.11 explícito
CMD ["python3.11", "-u", "handler.py"]