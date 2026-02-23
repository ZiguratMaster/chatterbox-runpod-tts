FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Evitar preguntas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# Instalar dependencias de sistema necesarias para audio y descargas
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Instalar Miniconda para gestionar Python 3.11 limpio
RUN curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
 && bash /tmp/miniconda.sh -b -p /opt/conda \
 && rm /tmp/miniconda.sh
ENV PATH=/opt/conda/bin:$PATH

# Crear entorno con Python 3.11
RUN conda create -y -n chatterbox python=3.11 && conda clean -afy

# Configurar shell para usar el entorno conda por defecto en los siguientes comandos
SHELL ["bash", "-lc"]

# Copiar e instalar requirements
COPY builder/requirements.txt /tmp/requirements.txt
RUN conda activate chatterbox \
 && pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# (OPCIONAL) Si tienes un audio local, descomenta estas lineas:
COPY assets/audio_ref_es_corto.wav /input/referencia.wav
ENV DEFAULT_AUDIO_PROMPT=/input/referencia.wav

# Copiar el código fuente
COPY src/ /src/

# Configurar caché de modelos en el volumen de red de Runpod (si existe)
ENV HF_HOME=/workspace/.cache/huggingface

# Comando de arranque: activa conda y lanza el handler
CMD ["bash", "-lc", "conda activate chatterbox && python -u /src/handler.py"]