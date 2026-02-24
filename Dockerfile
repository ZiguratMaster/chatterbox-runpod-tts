FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install runpod  # ← CRÍTICO
RUN pip install torch torchaudio fastapi uvicorn
RUN pip install -r requirements.txt

ENV HFHUB_ENABLE_HF_TRANSFER=0

EXPOSE 4123

# ← CMD CORRECTO para RunPod Serverless
CMD ["python", "handler.py"]  # Tu archivo con runpod.serverless.start