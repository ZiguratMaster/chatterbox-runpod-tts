FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala Torch compatible con CUDA 12.2 y chatterbox primero
RUN pip install --no-cache-dir \
    torch torchaudio --index-url https://download.pytorch.org/whl/cu121

COPY . /app

RUN pip install --no-cache-dir \
    runpod \
    soundfile librosa numpy requests pydantic \
    huggingface_hub \
    "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git"

ENV HF_HUB_ENABLE_HF_TRANSFER=0

EXPOSE 4123

CMD ["python", "handler.py"]