FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

ENV HFHUB_ENABLE_HF_TRANSFER=0

RUN uv sync --frozen --no-dev || pip install -r requirements.txt

EXPOSE 4123

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4123"]