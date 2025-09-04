# 🚀 TaskFlow Deployment Guide

## Option 1: Create Separate Repository (RECOMMENDED)

### Step 1: Initialize TaskFlow Repository
```bash
# Navigate to TaskFlow directory
cd /Users/jayminchang/coding/CS_Mastery_Sept2025/project_taskflow

# Initialize new git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: TaskFlow MVP with export, enhanced UI, and deployment config"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `taskflow`
3. Description: "Personal task management system with CLI, API, and web UI"
4. Public repository
5. **DON'T** initialize with README (we already have one)
6. Click "Create repository"

### Step 3: Push to GitHub
```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/jayminchanpgm/taskflow.git

# Push to main branch
git branch -M main
git push -u origin main
```

### Step 4: Deploy on Render.com
1. Go to https://render.com
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your `taskflow` repository
5. Configure:
   - Name: `taskflow-api`
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn my_taskflow.backend.api:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `PYTHON_VERSION` = `3.11.0`
6. Click "Create Web Service"

### Step 5: Update Frontend
Once deployed, update the frontend to use your production API:
```javascript
// In index_enhanced.html, change:
const API_URL = 'http://localhost:8000';
// To:
const API_URL = 'https://taskflow-api.onrender.com';
```

---

## Option 2: Deploy from Monorepo (Current Structure)

If you want to keep TaskFlow in CS_Mastery_Sept2025:

### Step 1: Push Updated Files
```bash
cd /Users/jayminchang/coding/CS_Mastery_Sept2025
git add .
git commit -m "Add TaskFlow deployment config and enhancements"
git push origin main
```

### Step 2: Deploy with Root Directory
1. Go to https://render.com
2. Connect your `CS_Mastery_Sept2025` repository
3. Configure:
   - Name: `taskflow-api`
   - Root Directory: `project_taskflow`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn my_taskflow.backend.api:app --host 0.0.0.0 --port $PORT`

---

## 🎉 After Deployment

Your TaskFlow will be available at:
- API: `https://taskflow-api.onrender.com`
- API Docs: `https://taskflow-api.onrender.com/docs`

### Testing Your Live API
```bash
# Test health check
curl https://taskflow-api.onrender.com/

# Get all tasks
curl https://taskflow-api.onrender.com/tasks/

# Export to JSON
curl https://taskflow-api.onrender.com/export/json
```

### Deployment Notes
- First deployment may take 5-10 minutes
- Free tier on Render spins down after inactivity (takes ~30s to wake up)
- Database will reset on each deployment (use PostgreSQL for persistence)

---

## 🐛 Troubleshooting

### If deployment fails:
1. Check build logs on Render dashboard
2. Ensure Python version is 3.11.0 or compatible
3. Verify all imports in api.py are correct
4. Check that requirements.txt has all dependencies

### Common issues:
- **Module not found**: Add missing package to requirements.txt
- **Port binding**: Ensure using `$PORT` environment variable
- **Path issues**: Check rootDir setting if using monorepo

---

## 📈 Next Steps After Deployment

1. Add custom domain (optional)
2. Set up PostgreSQL for persistent data
3. Add environment variables for sensitive data
4. Enable auto-deploy on git push
5. Set up monitoring (Render provides basic metrics)

---

**Need help?** The deployment logs on Render are very helpful for debugging!
