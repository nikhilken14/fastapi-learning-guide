FROM python:3.11-slim

WORKDIR /app

# Ensure logs output immediately to Docker stdout
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for consumed data API
EXPOSE 8001

CMD ["python", "main.py"]