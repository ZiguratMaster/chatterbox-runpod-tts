FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /workspace

# Instalar dependencias de audio (solo lo que falta)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN python3.11 -m pip install --no-cache-dir --upgrade pip

# Copiar requirements desde la raíz
COPY requirements.txt /requirements.txt
RUN python3.11 -m pip install --no-cache-dir -r /requirements.txt

# Copiar audio de referencia (opcional, quítalo si da problemas)
COPY audio_ref_es_corto.wav /input/referencia.wav
ENV DEFAULT_AUDIO_PROMPT=/input/referencia.wav

# Copiar el handler
COPY handler.py /src/handler.py

# Configurar caché de HuggingFace
ENV HF_HOME=/workspace/.cache/huggingface

# Comando de arranque (usa python3.11 explícito)
CMD ["python3.11", "-u", "/src/handler.py"]
