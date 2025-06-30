FROM python:3.11-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy /app code
COPY .. /app
WORKDIR /app

# Install Python dependencies
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

# Expose Flask port by default
EXPOSE 5000