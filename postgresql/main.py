# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
from routers111 import todo, auth

# ----------------- OpenTelemetry -----------------
import os
import logging

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from azure.monitor.opentelemetry.exporter import (
    AzureMonitorTraceExporter,
    AzureMonitorMetricExporter,
)

# ----------------- Azure Connection String -----------------
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if not connection_string:
    raise ValueError("❌ APPLICATIONINSIGHTS_CONNECTION_STRING not set in environment!")

# ----------------- Resource -----------------
resource = Resource.create({"service.name": "fastapi-backend"})

# ----------------- Tracing -----------------
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)
trace_exporter = AzureMonitorTraceExporter.from_connection_string(connection_string)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

# ----------------- Metrics -----------------
metric_exporter = AzureMonitorMetricExporter.from_connection_string(connection_string)
reader = PeriodicExportingMetricReader(metric_exporter)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter("fastapi-backend")
request_counter = meter.create_counter(
    name="requests.count",
    description="Number of requests received",
    unit="1"
)

# ----------------- FastAPI -----------------
app = FastAPI()

# Instrument FastAPI + Requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Setup a simple logger for your app
logger = logging.getLogger("fastapi-app")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# ----------------- Routes -----------------
@app.get("/health")
def health_check():
    logger.info("Health check called")
    request_counter.add(1, {"endpoint": "health"})
    return {"status": "ok"}

@app.get("/test-ai")
def test_ai():
    logger.info("Test AI event sent")
    request_counter.add(1, {"endpoint": "test-ai"})
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.close()
    conn.close()
    return {"status": "test sent"}

# ----------------- CORS -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Routers -----------------
app.include_router(todo.router)
app.include_router(auth.router)

# ----------------- Startup DB Init -----------------
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            role TEXT DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            owner INTEGER NOT NULL,
            CONSTRAINT fk_owner
                FOREIGN KEY(owner)
                    REFERENCES users(id)
                    ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ Database initialized and telemetry enabled")
