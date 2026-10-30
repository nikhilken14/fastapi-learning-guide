FROM python:3.11-slim

WORKDIR /app

# Ensure logs are emitted immediately to Docker stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies first to optimize Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

EXPOSE 8000

# Start Uvicorn pointing to the main FastAPI app instance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]