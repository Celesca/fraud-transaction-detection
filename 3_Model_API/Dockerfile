FROM python:3.11-slim

WORKDIR /app

# Install small set of system deps for common Python wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application code (context is the 3_Model_API folder)
COPY . /app

# Expose port
EXPOSE 8000

# Run with uvicorn using the module in this folder (server.py must expose `app`)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
