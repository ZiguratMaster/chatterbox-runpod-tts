FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

# Sistema + git
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia TODO (incluye voice-samplet.wav)
COPY . /app

# Dependencias
RUN pip install --no-cache-dir \
    torch torchaudio \
    runpod \
    soundfile librosa numpy \
    fastapi uvicorn pydantic \
    huggingface_hub[hf] \
    chatterbox-tts

# Desactiva hftransfer
ENV HFHUB_ENABLE_HF_TRANSFER=0

EXPOSE 4123

# Handler RunPod
CMD ["python", "handler.py"]