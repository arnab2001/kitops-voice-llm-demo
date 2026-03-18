FROM python:3.11-slim

WORKDIR /app

# System dependencies for audio processing and llama.cpp compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code only — model weights are mounted at runtime
# via volumes populated by `kit unpack`
COPY models/stt/src/ ./models/stt/src/
COPY models/stt/config.yaml ./models/stt/config.yaml
COPY models/llm/src/ ./models/llm/src/
COPY models/llm/config.yaml ./models/llm/config.yaml
COPY models/llm/prompts/ ./models/llm/prompts/
COPY models/tts/src/ ./models/tts/src/
COPY models/tts/config.yaml ./models/tts/config.yaml
COPY pipeline/ ./pipeline/

ENV PYTHONPATH=/app

EXPOSE 8765

CMD ["python", "pipeline/server.py"]
