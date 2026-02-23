FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /workspace

# Sistema
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# PyTorch ANTES de todo (crítico)
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install torch==2.4.1+cu121 torchaudio==2.4.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Runpod + resto
RUN python3 -m pip install runpod==1.7.6

# Chatterbox DESPUÉS de PyTorch
RUN python3 -m pip install chatterbox-tts transformers==4.44.2 tokenizers==0.20.1 safetensors numpy librosa

COPY handler.py /src/handler.py

ENV HF_HOME=/workspace/.cache/huggingface

CMD ["python3", "-u", "/src/handler.py"]