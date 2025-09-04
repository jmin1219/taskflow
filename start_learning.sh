#!/bin/bash
# Quick setup to start working on YOUR TaskFlow

echo "🎯 Setting up YOUR TaskFlow implementation..."

# Navigate to project
cd /Users/jayminchang/coding/CS_Mastery_Sept2025/project_taskflow

# Make sure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate it
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install sqlalchemy click rich pytest python-dotenv fastapi uvicorn

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 LEARNING PATH:"
echo "1. Start with: my_taskflow/backend/database.py"
echo "   Complete the 10 TODOs to build your database layer"
echo ""
echo "2. Then move to: my_taskflow/cli/taskflow.py"
echo "   Build your CLI commands one by one"
echo ""
echo "3. Finally: my_taskflow/tests/test_taskflow.py"
echo "   Write tests for your implementation"
echo ""
echo "📖 REFERENCE:"
echo "If you get stuck, check: reference_implementation/"
echo "But try to solve it yourself first!"
echo ""
echo "🚀 Open VS Code with: code ."
echo ""
echo "Good luck building YOUR TaskFlow! 💪"
