FROM runpod/base:0.6.2-cuda12.2.0

WORKDIR /app

# Sistema
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# Copiar todo el proyecto
COPY . /app

# Instalar con uv (recomendado por autores)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

RUN uv sync --frozen --no-dev

EXPOSE 4123

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4123"]