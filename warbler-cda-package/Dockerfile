# Warbler CDA - Production FastAPI Service for HuggingFace Spaces
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip \
    && rm -rf /root/.cache \
    && rm -rf /tmp/*

# Copy the warbler_cda module
COPY warbler_cda/ ./warbler_cda/

# Copy server startup script
COPY start_server.py ./

# Create packs directory (will be populated on first run)
RUN mkdir -p ./packs

# Set environment variables for HuggingFace Spaces
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=7860

# Expose HuggingFace Spaces default port
EXPOSE 7860

# Run the FastAPI server
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "7860"]