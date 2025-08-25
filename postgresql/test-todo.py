# todo.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_db_connection  # import DB helper

router = APIRouter()

class TodoItem(BaseModel):
    title: str
    description: str
    done: bool = False

@router.get("/")
def read_root():
    return {"message": "Welcome to the Todo API (PostgreSQL)"}

@router.get("/todos")
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, done FROM todos")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@router.post("/todos")
def add_todo(todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, done) VALUES (%s, %s, %s) RETURNING id",
        (todo.title, todo.description, todo.done)
    )
    todo_id = cursor.fetchone()["id"]
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "success", "id": todo_id}

@router.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET title = %s, description = %s, done = %s WHERE id = %s",
        (todo.title, todo.description, todo.done, todo_id)
    )
    updated_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if updated_rows == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"status": "updated"}

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    deleted_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    if deleted_rows == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"status": "deleted"}
