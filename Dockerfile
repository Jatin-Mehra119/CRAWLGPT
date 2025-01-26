# This Dockerfile is used to build a Docker image for the CrawlGPT project using Streamlit as the front-end
# Specifically for huggingface spaces

# Use Python 3.12 as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Chrome/Playwright dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    sudo \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set permissions
RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /app/.crawl4ai && chown -R appuser:appuser /app/.crawl4ai
RUN mkdir -p /app/exports && chown -R appuser:appuser /app/exports

# Copy project files
COPY pyproject.toml setup_env.py ./ 
COPY src/ ./src/
COPY tests/ ./tests/

# Gotta tweak some things in our main core code (LLMBasedCrowler.py) Comment out the following line:
# from dotenv import load_dotenv # line 11 It is not needed in the docker container 
# Because it's trying to load the API credentials from .env file which we don't have in the container


# Accept the secret token as a build argument
ARG GROQ_API_KEY
ARG OLLAMA_API_TOKEN

# Docs: https://huggingface.co/docs/hub/en/spaces-sdks-docker#secrets-and-variables-management

# Expose the secret GROQ_API_KEY and OLLAMA_API_TOKEN at build time and set them as environment variables
RUN --mount=type=secret,id=GROQ_API_KEY,mode=0444,required=true \
    export GROQ_API_KEY=$(cat /run/secrets/GROQ_API_KEY) && \
    echo "GROQ_API_KEY is set."
    
RUN --mount=type=secret,id=OLLAMA_API_TOKEN,mode=0444,required=true \
    export OLLAMA_API_TOKEN=$(cat /run/secrets/OLLAMA_API_TOKEN) && \
    echo "OLLAMA_API_TOKEN is set."

# Set environment variables using the build arguments
ENV OLLAMA_API_TOKEN=${OLLAMA_API_TOKEN}
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir pytest pytest-mockito black isort flake8

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/src:${PATH}"

# Switch to non-root user
USER appuser

# Allow appuser to install Python packages locally (user-level installations)
ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN mkdir -p /home/appuser/.local && chown -R appuser:appuser /home/appuser

# Install Playwright and dependencies
RUN playwright install 
RUN playwright install-deps

# Expose Streamlit port
EXPOSE 7860

# Set default command to run the Streamlit app
CMD ["python", "-m", "streamlit", "run", "src/crawlgpt/ui/chat_app.py", "--server.port=7860", "--server.address=0.0.0.0"]