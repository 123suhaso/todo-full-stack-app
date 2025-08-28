# -----------------------------
# Stage 1: Builder
# ------------------------------
FROM python:3.11 AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
# ✅ Use system install instead of --prefix
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------
# Stage 2: Production
# ------------------------------
FROM python:3.11

WORKDIR /app

# ✅ Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
