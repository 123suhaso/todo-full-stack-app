# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
from routers111 import todo, auth

# ----------------- OpenTelemetry -----------------
import logging
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter, AzureMonitorLogExporter

# Connection string (set via K8s env var)
connection_string = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
    "InstrumentationKey=4942b6f7-86ab-49a0-9c2b-26b022ab12cf;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/;ApplicationId=d53a3c36-7cd0-4f88-89e1-23436f79ffc2"
)

# Resource attributes
resource = Resource.create({"service.name": "fastapi-backend"})

# Setup tracing
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)

trace_exporter = AzureMonitorTraceExporter.from_connection_string(connection_string)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

# Setup logging
LoggingInstrumentor().instrument(set_logging_format=True)
log_exporter = AzureMonitorLogExporter.from_connection_string(connection_string)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------- FastAPI -----------------
app = FastAPI()

# Instrument FastAPI + Requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "ok"}

@app.get("/test-ai")
def test_ai():
    logger.info("Test event sent")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.close()
    conn.close()
    return {"status": "test sent"}


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(todo.router)
app.include_router(auth.router)

# Startup (DB init)
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
