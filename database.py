"""
TaskFlow Database - Deployment version
Copy for root level deployment
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

# Database URL - using local SQLite
DATABASE_URL = "sqlite:///taskflow.db"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Status Enum
class TaskStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"

# Priority Enum  
class Priority(enum.Enum):
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    NONE = 5

# Task Model
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="todo")
    priority = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }

# Project Model
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized!")

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
