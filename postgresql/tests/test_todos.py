import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from main import app, startup

from fastapi.testclient import TestClient

# Try importing based on where pytest is run from
try:
    from backend.main import app, startup
except ModuleNotFoundError:
    from main import app, startup

client = TestClient(app)

# Make sure DB is initialized before running tests
startup()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Todo API"}

def test_add_todo():
    response = client.post(
        "/todos",
        json={"title": "Test Task", "description": "Write tests", "done": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data

def test_get_todos():
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()
    assert isinstance(todos, list)
    assert len(todos) >= 1

def test_update_todo():
    # Create todo first
    create_res = client.post(
        "/todos",
        json={"title": "Update Me", "description": "Old", "done": False},
    )
    todo_id = create_res.json()["id"]

    # Update it
    update_res = client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated Title", "description": "New", "done": True},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "updated"

def test_delete_todo():
    # Create todo first
    create_res = client.post(
        "/todos",
        json={"title": "Delete Me", "description": "Temp", "done": False},
    )
    todo_id = create_res.json()["id"]

    # Delete it
    delete_res = client.delete(f"/todos/{todo_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"
