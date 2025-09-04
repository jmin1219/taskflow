#!/bin/bash
# Reorganize TaskFlow into reference and learning versions

echo "📚 Organizing TaskFlow for proper learning..."

BASE="/Users/jayminchang/coding/CS_Mastery_Sept2025/project_taskflow"
cd "$BASE"

# Create new structure
echo "Creating new folder structure..."

# Reference version (my implementation)
mkdir -p reference_implementation
mv backend reference_implementation/ 2>/dev/null
mv cli reference_implementation/ 2>/dev/null
mv taskflow reference_implementation/ 2>/dev/null
mv setup_tasks.py reference_implementation/ 2>/dev/null
mv taskflow.db reference_implementation/ 2>/dev/null
mv SUCCESS.md reference_implementation/ 2>/dev/null

# Your learning version with templates
mkdir -p my_taskflow
mkdir -p my_taskflow/backend
mkdir -p my_taskflow/cli
mkdir -p my_taskflow/tests

echo "✅ Folder structure created!"
echo ""
echo "📁 New Structure:"
echo "  reference_implementation/  (Complete working version for reference)"
echo "  my_taskflow/              (Your version with templates to fill in)"
echo ""
