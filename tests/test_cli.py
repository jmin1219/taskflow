"""
Test Suite for TaskFlow CLI
Testing Click CLI commands with pytest

RUN TESTS:
    pytest tests/test_cli.py -v
"""

import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import your CLI
from my_taskflow.cli.taskflow import cli
from my_taskflow.backend.database import Base, Task, SessionLocal, engine

# ===== TEST SETUP =====
runner = CliRunner()

@pytest.fixture(autouse=True)
def clear_database():
    """Clear database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """Provide a database session for tests"""
    session = SessionLocal()
    yield session
    session.close()

# ===== TEST ADD COMMAND =====
def test_add_basic_task():
    """Test adding a basic task"""
    result = runner.invoke(cli, ['add', 'Test Task'])
    assert result.exit_code == 0
    assert 'Added task' in result.output
    assert 'Test Task' in result.output

def test_add_task_with_priority():
    """Test adding a task with priority"""
    result = runner.invoke(cli, ['add', 'Important Task', '-p', '1'])
    assert result.exit_code == 0
    assert 'Priority: 1' in result.output

def test_add_task_with_due_date():
    """Test adding a task with due date"""
    result = runner.invoke(cli, ['add', 'Due Today', '-d', 'today'])
    assert result.exit_code == 0
    assert 'Due:' in result.output
    
    # Test tomorrow
    result = runner.invoke(cli, ['add', 'Due Tomorrow', '-d', 'tomorrow'])
    assert result.exit_code == 0
    assert 'Due:' in result.output
    
    # Test specific date
    future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    result = runner.invoke(cli, ['add', 'Future Task', '-d', future_date])
    assert result.exit_code == 0
    assert 'Due:' in result.output

def test_add_task_invalid_date():
    """Test adding a task with invalid date format"""
    result = runner.invoke(cli, ['add', 'Invalid Date Task', '-d', 'invalid-date'])
    assert 'Invalid date format' in result.output

# ===== TEST LIST COMMAND =====
def test_list_empty():
    """Test listing when no tasks exist"""
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'No tasks found' in result.output

def test_list_with_tasks(db_session):
    """Test listing tasks"""
    # Add tasks directly to database
    task1 = Task(title="Task 1", priority=1, status="todo")
    task2 = Task(title="Task 2", priority=2, status="done")
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()
    
    # List all tasks
    result = runner.invoke(cli, ['list', '--status', 'all'])
    assert result.exit_code == 0
    assert 'Task 1' in result.output
    assert 'Task 2' in result.output

def test_list_filter_by_status(db_session):
    """Test filtering tasks by status"""
    # Add tasks with different statuses
    todo_task = Task(title="Todo Task", status="todo")
    done_task = Task(title="Done Task", status="done")
    db_session.add(todo_task)
    db_session.add(done_task)
    db_session.commit()
    
    # List only todo tasks
    result = runner.invoke(cli, ['list', '--status', 'todo'])
    assert result.exit_code == 0
    assert 'Todo Task' in result.output
    assert 'Done Task' not in result.output

# ===== TEST DONE COMMAND =====
def test_done_command(db_session):
    """Test marking a task as done"""
    # Add a task
    task = Task(title="Test Task", status="todo")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Mark as done
    result = runner.invoke(cli, ['done', str(task_id)])
    assert result.exit_code == 0
    assert f'Task #{task_id} marked as done' in result.output

def test_done_nonexistent_task():
    """Test marking non-existent task as done"""
    result = runner.invoke(cli, ['done', '999'])
    assert 'not found' in result.output

def test_done_already_done(db_session):
    """Test marking already done task"""
    # Add a done task
    task = Task(title="Already Done", status="done")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Try to mark as done again
    result = runner.invoke(cli, ['done', str(task_id)])
    assert result.exit_code == 0
    assert 'already done' in result.output.lower()

# ===== TEST DELETE COMMAND =====
def test_delete_with_confirmation(db_session):
    """Test deleting a task with confirmation"""
    # Add a task
    task = Task(title="Task to Delete")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Delete with confirmation (respond 'y')
    result = runner.invoke(cli, ['delete', str(task_id)], input='y\n')
    assert result.exit_code == 0
    assert 'deleted successfully' in result.output

def test_delete_with_skip_confirmation(db_session):
    """Test deleting a task skipping confirmation"""
    # Add a task
    task = Task(title="Task to Delete")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Delete with -y flag
    result = runner.invoke(cli, ['delete', str(task_id), '-y'])
    assert result.exit_code == 0
    assert 'deleted successfully' in result.output

def test_delete_cancelled(db_session):
    """Test cancelling task deletion"""
    # Add a task
    task = Task(title="Keep This Task")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Try to delete but cancel (respond 'n')
    result = runner.invoke(cli, ['delete', str(task_id)], input='n\n')
    assert result.exit_code == 0
    assert 'Cancelled' in result.output

def test_delete_nonexistent():
    """Test deleting non-existent task"""
    result = runner.invoke(cli, ['delete', '999', '-y'])
    assert 'not found' in result.output

# ===== TEST TODAY COMMAND =====
def test_today_command_empty():
    """Test today command with no tasks"""
    result = runner.invoke(cli, ['today'])
    assert result.exit_code == 0
    assert 'TODAY' in result.output

def test_today_command_with_tasks(db_session):
    """Test today command with various tasks"""
    # Add tasks with different due dates
    today = datetime.now()
    today_task = Task(
        title="Due Today",
        due_date=today.replace(hour=23, minute=59)
    )
    overdue_task = Task(
        title="Overdue Task",
        due_date=today - timedelta(days=1),
        status="todo"
    )
    tomorrow_task = Task(
        title="Due Tomorrow",
        due_date=today + timedelta(days=1)
    )
    in_progress = Task(
        title="In Progress Task",
        status="in_progress"
    )
    
    db_session.add(today_task)
    db_session.add(overdue_task)
    db_session.add(tomorrow_task)
    db_session.add(in_progress)
    db_session.commit()
    
    # Run today command
    result = runner.invoke(cli, ['today'])
    assert result.exit_code == 0
    assert 'Due Today' in result.output
    assert 'Overdue Task' in result.output
    assert 'In Progress Task' in result.output
    assert 'Due Tomorrow' not in result.output  # Should not show tomorrow's task

def test_today_stats(db_session):
    """Test that today command shows statistics"""
    # Add some tasks
    for i in range(3):
        task = Task(title=f"Task {i}", status="todo")
        db_session.add(task)
    db_session.commit()
    
    result = runner.invoke(cli, ['today'])
    assert result.exit_code == 0
    assert 'STATS' in result.output
    assert 'Total in backlog' in result.output

# ===== TEST EDIT COMMAND =====
def test_edit_title(db_session):
    """Test editing task title"""
    # Add a task
    task = Task(title="Original Title")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Edit title
    result = runner.invoke(cli, ['edit', str(task_id), '--title', 'New Title'])
    assert result.exit_code == 0
    assert 'updated successfully' in result.output
    assert 'New Title' in result.output

def test_edit_priority(db_session):
    """Test editing task priority"""
    # Add a task
    task = Task(title="Test Task", priority=3)
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Edit priority
    result = runner.invoke(cli, ['edit', str(task_id), '--priority', '1'])
    assert result.exit_code == 0
    assert 'Priority: 3 → 1' in result.output or '3 → 1' in result.output

def test_edit_status(db_session):
    """Test editing task status"""
    # Add a task
    task = Task(title="Test Task", status="todo")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Edit status
    result = runner.invoke(cli, ['edit', str(task_id), '--status', 'in_progress'])
    assert result.exit_code == 0
    assert 'in_progress' in result.output

def test_edit_multiple_fields(db_session):
    """Test editing multiple fields at once"""
    # Add a task
    task = Task(title="Old", priority=5, status="todo")
    db_session.add(task)
    db_session.commit()
    task_id = task.id
    
    # Edit multiple fields
    result = runner.invoke(cli, [
        'edit', str(task_id),
        '--title', 'New',
        '--priority', '1',
        '--status', 'done'
    ])
    assert result.exit_code == 0
    assert 'updated successfully' in result.output

def test_edit_no_changes():
    """Test edit command with no changes specified"""
    runner.invoke(cli, ['add', 'Test Task'])
    result = runner.invoke(cli, ['edit', '1'])
    assert 'No changes specified' in result.output

def test_edit_nonexistent():
    """Test editing non-existent task"""
    result = runner.invoke(cli, ['edit', '999', '--title', 'New'])
    assert 'not found' in result.output

# ===== TEST INTEGRATION =====
def test_full_workflow():
    """Test a complete workflow: add, list, done, delete"""
    # Add a task
    add_result = runner.invoke(cli, ['add', 'Integration Test', '-p', '1'])
    assert add_result.exit_code == 0
    
    # List tasks
    list_result = runner.invoke(cli, ['list'])
    assert list_result.exit_code == 0
    assert 'Integration Test' in list_result.output
    
    # Mark as done (assuming it's task #1)
    done_result = runner.invoke(cli, ['done', '1'])
    assert done_result.exit_code == 0
    
    # List done tasks
    done_list = runner.invoke(cli, ['list', '--status', 'done'])
    assert 'Integration Test' in done_list.output
    
    # Delete the task
    delete_result = runner.invoke(cli, ['delete', '1', '-y'])
    assert delete_result.exit_code == 0
    
    # Verify it's gone
    final_list = runner.invoke(cli, ['list', '--status', 'all'])
    assert 'No tasks found' in final_list.output

# ===== RUN TESTS =====
if __name__ == "__main__":
    """
    Run tests from command line:
    python -m pytest tests/test_cli.py -v
    """
    pytest.main([__file__, "-v"])
