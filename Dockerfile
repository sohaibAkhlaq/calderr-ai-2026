FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy simple requirements
COPY requirements-simple.txt requirements.txt

# Upgrade pip and install with dependency resolution
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --timeout=1000 -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]
