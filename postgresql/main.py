# main.p
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
from routers111 import todo, auth  # import your router

app = FastAPI()

app.get("/health")
def health_check():
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
