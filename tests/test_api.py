"""
Test Suite for TaskFlow API
Learn pytest while testing your FastAPI backend!

RUN TESTS:
    pytest tests/test_api.py -v
    
RUN WITH COVERAGE:
    pytest tests/test_api.py --cov=my_taskflow.backend.api
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import your app and database models
from my_taskflow.backend.api import app, get_db
from my_taskflow.backend.database import Base, Task

# ===== TEST SETUP =====
# Create a test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Test database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the database dependency with test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency in the app
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# ===== FIXTURES =====
@pytest.fixture
def sample_task():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": 1,
        "due_date": (datetime.now() + timedelta(days=1)).isoformat()
    }

@pytest.fixture(autouse=True)
def clear_database():
    """Clear database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test if needed

# ===== TEST HEALTH CHECK =====
def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "running"

# ===== TEST CREATE TASK =====
def test_create_task(sample_task):
    """Test creating a new task"""
    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 200
    data = response.json()
    
    # Check response contains expected fields
    assert data["title"] == sample_task["title"]
    assert data["priority"] == sample_task["priority"]
    assert "id" in data
    assert data["status"] == "todo"  # Default status

def test_create_task_minimal():
    """Test creating a task with minimal data"""
    minimal_task = {"title": "Minimal Task"}
    response = client.post("/tasks/", json=minimal_task)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["priority"] == 3  # Default priority

def test_create_task_invalid():
    """Test creating a task with invalid data"""
    invalid_task = {"priority": 1}  # Missing required title
    response = client.post("/tasks/", json=invalid_task)
    assert response.status_code == 422  # Validation error

# ===== TEST GET TASKS =====
def test_get_tasks_empty():
    """Test getting tasks when database is empty"""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_data(sample_task):
    """Test getting tasks after creating some"""
    # Create 3 tasks
    for i in range(3):
        task = sample_task.copy()
        task["title"] = f"Task {i+1}"
        client.post("/tasks/", json=task)
    
    # Get all tasks
    response = client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert all("id" in task for task in tasks)

def test_get_tasks_with_status_filter():
    """Test filtering tasks by status"""
    # Create tasks with different statuses
    task1 = {"title": "Todo Task", "status": "todo"}
    task2 = {"title": "Done Task"}
    
    response1 = client.post("/tasks/", json=task1)
    task_id = response1.json()["id"]
    client.post("/tasks/", json=task2)
    
    # Mark first task as done
    client.post(f"/tasks/{task_id}/done")
    
    # Filter by status
    response = client.get("/tasks/?status=done")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "done"

# ===== TEST GET SINGLE TASK =====
def test_get_single_task(sample_task):
    """Test getting a specific task by ID"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]
    
    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task["title"]

def test_get_nonexistent_task():
    """Test getting a task that doesn't exist"""
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# ===== TEST UPDATE TASK =====
def test_update_task(sample_task):
    """Test updating a task"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]
    
    # Update the task
    update_data = {
        "title": "Updated Task",
        "priority": 5,
        "status": "in_progress"
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["priority"] == 5
    assert data["status"] == "in_progress"

def test_partial_update_task(sample_task):
    """Test partially updating a task"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]
    original_title = create_response.json()["title"]
    
    # Update only status
    update_data = {"status": "done"}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["title"] == original_title  # Title unchanged

# ===== TEST DELETE TASK =====
def test_delete_task(sample_task):
    """Test deleting a task"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify it's deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_task():
    """Test deleting a task that doesn't exist"""
    response = client.delete("/tasks/999")
    assert response.status_code == 404

# ===== TEST TODAY'S TASKS =====
def test_get_todays_tasks():
    """Test getting today's tasks"""
    # Create tasks with different due dates
    today_task = {
        "title": "Today's Task",
        "due_date": datetime.now().isoformat()
    }
    tomorrow_task = {
        "title": "Tomorrow's Task",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat()
    }
    
    client.post("/tasks/", json=today_task)
    client.post("/tasks/", json=tomorrow_task)
    
    # Get today's tasks
    response = client.get("/tasks/today/")
    assert response.status_code == 200
    tasks = response.json()
    # Should include today's task
    assert any(task["title"] == "Today's Task" for task in tasks)

# ===== TEST MARK AS DONE =====
def test_mark_task_done(sample_task):
    """Test marking a task as done"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]
    
    # Mark as done
    response = client.post(f"/tasks/{task_id}/done")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"

def test_mark_already_done_task():
    """Test marking an already done task"""
    # Create and mark task as done
    create_response = client.post("/tasks/", json={"title": "Test"})
    task_id = create_response.json()["id"]
    client.post(f"/tasks/{task_id}/done")
    
    # Try to mark as done again
    response = client.post(f"/tasks/{task_id}/done")
    assert response.status_code == 400
    assert "already done" in response.json()["detail"].lower()

# ===== TEST STATS ENDPOINT =====
def test_get_stats():
    """Test the stats endpoint"""
    # Create tasks with different statuses
    client.post("/tasks/", json={"title": "Todo 1"})
    client.post("/tasks/", json={"title": "Todo 2"})
    
    create_response = client.post("/tasks/", json={"title": "Done Task"})
    task_id = create_response.json()["id"]
    client.post(f"/tasks/{task_id}/done")
    
    # Get stats
    response = client.get("/stats/")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_tasks"] == 3
    assert stats["by_status"]["todo"] == 2
    assert stats["by_status"]["done"] == 1
    assert "completion_rate" in stats

# ===== TEST EDGE CASES =====
def test_task_with_past_due_date():
    """Test creating a task with past due date (overdue)"""
    overdue_task = {
        "title": "Overdue Task",
        "due_date": (datetime.now() - timedelta(days=1)).isoformat()
    }
    response = client.post("/tasks/", json=overdue_task)
    assert response.status_code == 200
    # Task should be created even if overdue

def test_task_priority_boundaries():
    """Test priority value boundaries"""
    # Test minimum priority
    min_task = {"title": "Min Priority", "priority": 1}
    response = client.post("/tasks/", json=min_task)
    assert response.status_code == 200
    assert response.json()["priority"] == 1
    
    # Test maximum priority
    max_task = {"title": "Max Priority", "priority": 5}
    response = client.post("/tasks/", json=max_task)
    assert response.status_code == 200
    assert response.json()["priority"] == 5

# ===== RUN TESTS =====
if __name__ == "__main__":
    """
    Run tests from command line:
    python -m pytest tests/test_api.py -v
    
    Or with coverage:
    pip install pytest-cov
    python -m pytest tests/test_api.py --cov=my_taskflow.backend.api --cov-report=html
    """
    pytest.main([__file__, "-v"])
