FROM runpod/pytorch:2.1.0-py3.10-cuda11.8-devel-ubuntu22.04

RUN apt-get update && apt-get install -y ffmpeg git build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install torch==2.1.0+cu118 torchaudio==2.1.0+cu118 \
    --extra-index-url https://download.pytorch.org/whl/cu118

RUN pip install -U pip setuptools wheel
RUN pip install --no-cache-dir TTS==0.13.4

RUN pip install runpod

COPY handler.py /handler.py
CMD ["python", "/handler.py"]