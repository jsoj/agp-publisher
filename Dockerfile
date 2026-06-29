FROM python:3.11-slim

# Set timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

# Install system dependencies (build-essential for potential compilation, though usually not needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY autonomous_publisher.py .
COPY scheduler.py .
COPY PROMPTS.md .

# Create directory for persisted database volume
RUN mkdir -p /app/data

CMD ["python", "scheduler.py"]
