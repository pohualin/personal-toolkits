FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY crontab /app/crontab

# Create directories for outputs
RUN mkdir -p /app/data/customer_sync \
    /app/data/analysis \
    /app/data/repos \
    /app/weekly_report

# Set Python path
ENV PYTHONPATH=/app