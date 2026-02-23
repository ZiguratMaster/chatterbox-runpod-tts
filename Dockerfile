FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# Instalar PyTorch PRIMERO (crítico para Chatterbox)
COPY pytorch-req.txt /tmp/pytorch-req.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/pytorch-req.txt

# Resto de dependencias
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY handler.py /src/handler.py

ENV HF_HOME=/workspace/.cache/huggingface

CMD ["python3", "-u", "/src/handler.py"]