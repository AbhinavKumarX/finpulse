FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# HuggingFace Spaces uses port 7860
EXPOSE 7860

# Use /data for persistent storage on HF Spaces (persists across restarts)
# Falls back to /app/data locally
ENV DB_DIR=/data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
