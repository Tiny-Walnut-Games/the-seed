# Use an official Python runtime as a parent image
FROM python:alpine3.22

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt (if present)
RUN if [ -f scripts/requirements.txt ]; then pip install --no-cache-dir -r scripts/requirements.txt; fi

# Install requests for LLM communication
RUN pip install requests

# Expose ports for web/API services and LLM communication
EXPOSE 8080 9998

# Environment variables for LLM integration
ENV LLM_BRIDGE_MODE=gemma3
ENV LLM_ENDPOINT=http://host.docker.internal:9998
ENV WARBLER_AI_ENABLED=true

# Make scripts executable
RUN chmod +x scripts/*.py

# Default command to run TLDA with Warbler-Gemma3 integration
CMD ["python", "scripts/warbler_gemma3_bridge.py"]

# ---
# Build: docker build -t twg-tlda-ai .
# Run: docker run --rm -p 8080:8080 twg-tlda-ai
#
# For development with shell access:
# docker run -it --rm -p 8080:8080 twg-tlda-ai bash
