# main.p
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
from routers111 import todo, auth  # import your router

# ------------------- Azure Application Insights -------------------
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

# Replace with your actual Instrumentation Key (from Application Insights)
INSTRUMENTATION_KEY = "4942b6f7-86ab-49a0-9c2b-26b022ab12cf"

# Logging setup
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=f"InstrumentationKey={INSTRUMENTATION_KEY}")
)

# Tracing setup
exporter = AzureExporter(connection_string=f"InstrumentationKey={INSTRUMENTATION_KEY}")
tracer = Tracer(exporter=exporter, sampler=ProbabilitySampler(1.0))


app = FastAPI()

@app.get("/health")
def health_check():
    logger.warning("Health check called")  # logged to App Insights
    return {"status": "ok"}



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todo.router)
app.include_router(auth.router)

# Initialize DB on startup
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ Create users table
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

    # 2️⃣ Create todos table with owner FK
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
