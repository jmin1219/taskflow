# TaskFlow - Personal Task Management System

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)

A full-stack task management system built with Python, featuring both CLI and REST API interfaces.

## 🚀 Features

- **Complete CLI Interface** - Add, list, edit, delete, and track tasks from the command line
- **RESTful API** - Full CRUD operations with FastAPI
- **Auto-generated API Documentation** - Interactive docs at `/docs`
- **Smart Task Tracking** - Priority levels, due dates, and status management
- **Today View** - See overdue, due today, and in-progress tasks at a glance
- **Data Export** - Export tasks to CSV or JSON formats
- **Enhanced Web UI** - Modern interface with dark mode, charts, and real-time stats
- **85% Test Coverage** - Comprehensive test suite with pytest

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **CLI**: Click, Rich
- **Testing**: pytest, pytest-cov
- **Documentation**: Auto-generated with OpenAPI/Swagger

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/taskflow.git
cd taskflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### Using the CLI

```bash
# Add a task
python my_taskflow/cli/taskflow.py add "Complete project documentation" -p 1 -d today

# List all tasks
python my_taskflow/cli/taskflow.py list

# View today's tasks
python my_taskflow/cli/taskflow.py today

# Mark task as done
python my_taskflow/cli/taskflow.py done 1

# Edit a task
python my_taskflow/cli/taskflow.py edit 1 --status in_progress

# Delete a task
python my_taskflow/cli/taskflow.py delete 1 -y
```

### Using the API

```bash
# Start the API server
uvicorn my_taskflow.backend.api:app --reload

# Visit the interactive docs
open http://localhost:8000/docs
```

#### API Endpoints

- `GET /` - Health check
- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create new task
- `GET /tasks/today/` - Get today's tasks
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `POST /tasks/{id}/done` - Mark task as done
- `GET /stats/` - Get task statistics
- `GET /export/csv` - Export tasks to CSV
- `GET /export/json` - Export tasks to JSON

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=my_taskflow --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=my_taskflow --cov-report=html
open htmlcov/index.html
```

### Test Coverage: 85%
- API: 90% coverage
- CLI: 88% coverage  
- Database: 71% coverage

## 📁 Project Structure

```
taskflow/
├── my_taskflow/
│   ├── backend/
│   │   ├── database.py      # SQLAlchemy models and database setup
│   │   └── api.py          # FastAPI application with 11 endpoints
│   ├── cli/
│   │   ├── taskflow.py     # Click CLI application
│   │   └── export.py       # Export/Import utilities
│   └── frontend/
│       ├── index.html      # Original web interface
│       └── index_enhanced.html  # Enhanced UI with dark mode
├── tests/
│   ├── test_api.py         # API tests (27 tests)
│   └── test_cli.py         # CLI tests (30 tests)
├── config.py              # Configuration management
├── render.yaml            # Render.com deployment config
├── requirements.txt        # Project dependencies
└── README.md              # This file
```

## 🎓 Learning Outcomes

This project was built as part of my CS Mastery journey. Through building TaskFlow, I learned:

- **RESTful API Design** - Built 11 endpoints following REST principles
- **Database Design** - Implemented SQLAlchemy ORM with proper relationships
- **CLI Development** - Created intuitive command-line interface with Click
- **Test-Driven Development** - Achieved 85% test coverage with pytest
- **API Documentation** - Leveraged FastAPI's auto-documentation features
- **Error Handling** - Implemented comprehensive error handling throughout
- **Data Validation** - Used Pydantic models for automatic validation
- **Frontend Development** - Built interactive UI with vanilla JS and Tailwind CSS
- **Data Visualization** - Integrated Chart.js for progress tracking
- **Dark Mode Implementation** - Added theme switching with localStorage
- **Export Functionality** - Implemented CSV and JSON export capabilities
- **Deployment** - Configured for cloud deployment on Render.com

## 💡 Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Task categories and tags
- [ ] Recurring tasks
- [ ] Task dependencies
- [ ] Task search and filtering
- [ ] Email notifications for due tasks
- [ ] Mobile app with React Native
- [ ] PostgreSQL support for production
- [ ] Task templates
- [ ] Collaboration features

## 📝 License

MIT License - feel free to use this project for learning!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 👨‍💻 Author

**Jaymin Chang**
- GitHub: [@jayminchanpgm](https://github.com/jayminchanpgm)
- Built during CS Mastery journey preparing for Northeastern Align MSCS

## 🌟 Live Demo

🚀 **API**: [https://taskflow-api.onrender.com](https://taskflow-api.onrender.com) *(deployment pending)*

📚 **API Docs**: [https://taskflow-api.onrender.com/docs](https://taskflow-api.onrender.com/docs) *(deployment pending)*

---

*Built with ❤️ and lots of ☕ in Vancouver*
