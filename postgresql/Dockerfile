# -----------------------------
# Stage 1: Builder
# ------------------------------
FROM python:3.11 AS builder

WORKDIR /app

# Install build dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies in isolated location
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ------------------------------
# Stage 2: Production
# ------------------------------
FROM python:3.11

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI directly (no internal wait)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
