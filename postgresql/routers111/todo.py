# todo.py
from fastapi import APIRouter, HTTPException, Depends
import psycopg2
import psycopg2.extras
from db import get_db_connection
from pydantic import BaseModel
from .auth import get_current_user
# import JWT authentication function

router = APIRouter()

# =====================
# Pydantic Model
# =====================
class TodoItem(BaseModel):
    title: str
    description: str
    done: bool = False

# =====================
# Routes
# =====================

@router.get("/")
def read_root():
    return {"message": "Welcome to the Todo API (PostgreSQL)"}

@router.get("/todos")
def get_todos(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]  # get current user's ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, done, owner FROM todos WHERE owner = %s",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@router.post("/todos")
def add_todo(todo: TodoItem, current_user: dict = Depends(get_current_user)):
    owner_id = current_user["id"]  # use ID from JWT
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        """
        INSERT INTO todos (title, description, done, owner) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id
        """,
        (todo.title, todo.description, todo.done, owner_id)
    )
    todo_row = cursor.fetchone()  # returns dict
    conn.commit()
    cursor.close()
    conn.close()

    if not todo_row:
        raise HTTPException(status_code=500, detail="Failed to create todo")

    return {"status": "success", "id": todo_row["id"]}


@router.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoItem, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE todos 
        SET title = %s, description = %s, done = %s
        WHERE id = %s AND owner = %s
        """,
        (todo.title, todo.description, todo.done, todo_id, user_id)
    )
    updated_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="Todo not found or not owned by you")
    return {"status": "updated"}

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM todos WHERE id = %s AND owner = %s",
        (todo_id, user_id)
    )
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="Todo not found or not owned by you")
    return {"status": "deleted"}
