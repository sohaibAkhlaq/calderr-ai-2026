# Dockerfile for Autonomous AI Research Lab

FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app

EXPOSE 8000
EXPOSE 8501

CMD ["python", "cli.py"]
