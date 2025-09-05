#!/usr/bin/env python3
"""
TaskFlow API - Direct import version for Render deployment
This file combines the necessary imports to avoid module path issues
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import sys
import os
from pathlib import Path

# Import database from same directory (both at root now)
from database import Task, SessionLocal, init_db, TaskStatus, Priority

# ===== Setup Lifespan for Startup Events =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("✅ Database initialized!")
    yield
    # Shutdown (if needed)
    pass

# ===== Create FastAPI App =====
app = FastAPI(
    title="TaskFlow API",
    description="A personal task management system built with FastAPI",
    version="0.1.0",
    lifespan=lifespan
)

# ===== Add CORS Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Database Dependency =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== Pydantic Models =====
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 3
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

# ===== Mount static files for frontend =====
# Check if frontend directory exists
frontend_path = Path(__file__).parent / "my_taskflow" / "frontend"
root_frontend_path = Path(__file__).parent  # Also check root for frontend files

# Try to find the frontend HTML
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# ===== Root Endpoint - Serve HTML =====
@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Serve the frontend HTML instead of JSON
    """
    # First try production HTML in root
    html_file = root_frontend_path / "frontend_production.html"
    
    if not html_file.exists():
        # Then try enhanced HTML in frontend folder
        html_file = frontend_path / "index_enhanced.html" 
    
    if not html_file.exists():
        # Fallback to basic index.html
        html_file = frontend_path / "index.html"
    
    if html_file.exists():
        with open(html_file, 'r') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        # Fallback to a simple HTML if no file found
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>TaskFlow</title>
                <style>
                    body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
                    h1 { color: #2563eb; }
                    .links { margin-top: 30px; }
                    .links a { display: inline-block; margin: 10px; padding: 10px 20px; 
                              background: #3b82f6; color: white; text-decoration: none; 
                              border-radius: 5px; }
                    .links a:hover { background: #2563eb; }
                </style>
            </head>
            <body>
                <h1>🚀 TaskFlow API</h1>
                <p>Welcome to TaskFlow - Your Personal Task Management System!</p>
                <div class="links">
                    <a href="/docs">📚 API Documentation</a>
                    <a href="/api/health">❤️ Health Check</a>
                </div>
                <p style="margin-top: 30px; color: #666;">Frontend files not found. API is working!</p>
            </body>
        </html>
        """)

# ===== Health Check Endpoint =====
@app.get("/api/health")
def health_check():
    """
    API health check endpoint
    """
    return {
        "message": "Welcome to TaskFlow API!",
        "status": "running",
        "docs": "Visit /docs for interactive documentation"
    }

# ===== Create Task =====
@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ===== Get All Tasks =====
@app.get("/tasks/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.limit(limit).all()
    return tasks

# ===== Get Single Task =====
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

# ===== Update Task =====
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

# ===== Delete Task =====
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task_title = task.title
    db.delete(task)
    db.commit()
    
    return {
        "message": f"Task {task_id} deleted successfully",
        "task_title": task_title
    }

# ===== Today's Tasks =====
@app.get("/tasks/today/", response_model=List[TaskResponse])
def get_todays_tasks(db: Session = Depends(get_db)):
    from datetime import datetime, time
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59)
    
    tasks = db.query(Task).filter(
        (Task.due_date.between(today_start, today_end)) |
        (Task.status == "in_progress")
    ).all()
    
    return tasks

# ===== Mark Task as Done =====
@app.post("/tasks/{task_id}/done", response_model=TaskResponse)
def mark_task_done(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if task.status == "done":
        raise HTTPException(status_code=400, detail="Task is already done")
    
    task.status = "done"
    db.commit()
    db.refresh(task)
    return task

# ===== Export Tasks (CSV) =====
@app.get("/export/csv")
def export_tasks_csv(status: Optional[str] = None, db: Session = Depends(get_db)):
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.all()
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'title', 'description', 'priority', 'status', 'due_date', 'created_at'])
    
    writer.writeheader()
    for task in tasks:
        writer.writerow({
            'id': task.id,
            'title': task.title,
            'description': task.description or '',
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date.isoformat() if task.due_date else '',
            'created_at': task.created_at.isoformat()
        })
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=taskflow_export.csv'}
    )

# ===== Export Tasks (JSON) =====
@app.get("/export/json")
def export_tasks_json(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        })
    
    return tasks_data

# ===== Stats Endpoint =====
@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()
    todo_tasks = db.query(Task).filter(Task.status == "todo").count()
    in_progress = db.query(Task).filter(Task.status == "in_progress").count()
    done_tasks = db.query(Task).filter(Task.status == "done").count()
    
    from datetime import datetime
    overdue = db.query(Task).filter(
        Task.due_date < datetime.now(),
        Task.status != "done"
    ).count()
    
    return {
        "total_tasks": total_tasks,
        "by_status": {
            "todo": todo_tasks,
            "in_progress": in_progress,
            "done": done_tasks
        },
        "overdue_tasks": overdue,
        "completion_rate": f"{(done_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "0%"
    }

# ===== Main entry point =====
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
