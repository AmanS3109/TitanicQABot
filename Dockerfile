# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run data preparation
RUN python prepare_data.py

# Expose ports (FastAPI on 8000, Streamlit on 8501)
EXPOSE 8000 8501

# Set environment variables
ENV BACKEND_URL=http://localhost:8000
ENV PYTHONUNBUFFERED=1

# Make script executable and run it
RUN chmod +x start.sh
CMD ["./start.sh"]
