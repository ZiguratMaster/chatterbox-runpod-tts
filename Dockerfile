FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

# Instala git Y deps sistema PRIMERO
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

# Usa --extra-index-url (NO --index-url) + sin pin versión
RUN python3.11 -m pip install --no-cache-dir \
    hf_transfer \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch torchaudio \
    runpod \
    soundfile librosa numpy requests pydantic \
    huggingface_hub \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=1

EXPOSE 4123

CMD ["python3.11", "-u", "handler.py"]