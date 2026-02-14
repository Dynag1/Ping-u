FROM python:3.11-slim

# Install system dependencies
# iputils-ping: required for the ping command used by Pingu.py
# tzdata: required for correct timezone handling in logs
# net-tools & curl: useful tools for debugging
RUN apt-get update && apt-get install -y \
    iputils-ping \
    net-tools \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the rest of the application
COPY . .

# Create directories for persistent data (volumes)
RUN mkdir -p bd config logs certs

# Expose the web administration port
EXPOSE 9090

# Set default timezone (can be overridden in docker-compose)
ENV TZ=Europe/Paris

# Run the application in headless mode
CMD ["python", "Pingu.py", "--headless"]
