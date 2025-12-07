# Use a lightweight Python version
FROM python:3.10-slim

# Install system dependencies (FFmpeg is required for audio)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]