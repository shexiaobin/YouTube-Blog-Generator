FROM python:3.9-slim

# Install system dependencies (ffmpeg is required for yt-dlp audio extraction)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production
RUN pip install gunicorn

# Copy application code
COPY . .

# Create necessary directories for runtime
RUN mkdir -p output/blogs output/audio

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5001

# Expose the port
EXPOSE 5001

# Run the application with Gunicorn
# 1 worker, 2 threads (since we have async IO tasks)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
