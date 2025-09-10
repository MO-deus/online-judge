# Use Python as base (lightweight, easy for orchestration)
FROM python:3.11-slim

# Install required compilers/interpreters
RUN apt-get update && apt-get install -y \
    g++ \
    default-jdk \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .

# Expose port (for Flask/FastAPI server inside container)
EXPOSE 8080

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
