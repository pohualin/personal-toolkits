FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command (adjust as needed)
CMD ["python", "scripts/main.py"]