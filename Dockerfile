FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    pkg-config \
    cmake \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # Install fairseq separately
    pip install torch && \
    pip install git+https://github.com/pytorch/fairseq.git@v0.10.2#egg=fairseq

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p data/models logs nginx/ssl static configs

# Set environment variables
ENV MODEL_PATH=/app/data/models/best_model.pt
ENV CONFIG_PATH=/app/configs/config.json
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]