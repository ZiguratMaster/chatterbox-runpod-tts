FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Evitar preguntas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# Instalar Python 3.11 y dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-pip \
    python3.11-venv \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Crear symlink para python -> python3.11
RUN ln -s /usr/bin/python3.11 /usr/bin/python \
 && ln -s /usr/bin/python3.11 /usr/bin/python3 \
 && ln -s /usr/bin/pip3.11 /usr/bin/pip

# Actualizar pip
RUN pip install --no-cache-dir --upgrade pip

# Copiar e instalar requirements desde la raíz
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar audio de referencia (opcional, quítalo si da problemas)
COPY audio_ref_es_corto.wav /input/referencia.wav
ENV DEFAULT_AUDIO_PROMPT=/input/referencia.wav

# Copiar el handler desde la raíz
COPY handler.py /src/handler.py

# Configurar caché de HuggingFace
ENV HF_HOME=/workspace/.cache/huggingface

# Comando de arranque
CMD ["python", "-u", "/src/handler.py"]