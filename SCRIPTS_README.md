# Enhanced Purview CLI v2.0 - PowerShell Scripts

This directory contains PowerShell scripts to help you run and verify the Enhanced Purview CLI v2.0 full-stack application.

## Available Scripts

### 🚀 `run-full-stack.ps1` - Main Application Runner
Comprehensive script to start both backend (FastAPI) and frontend (React) services.

```powershell
# Start full stack in development mode
.\run-full-stack.ps1

# Start only backend
.\run-full-stack.ps1 -BackendOnly

# Start only frontend  
.\run-full-stack.ps1 -FrontendOnly

# Production mode
.\run-full-stack.ps1 -Mode prod

# Clean build artifacts and start
.\run-full-stack.ps1 -Clean

# Skip dependency installation
.\run-full-stack.ps1 -SkipInstall

# Custom ports
.\run-full-stack.ps1 -BackendPort 8080 -FrontendPort 3001
```

**Features:**
- Automatic port detection and fallback
- Health checks for both services
- Environment setup and dependency installation
- Parallel service execution
- Graceful shutdown handling
- Production and development modes

### ⚡ `quick-start.ps1` - Simple Test Runner
Quick script for basic testing and individual service startup.

```powershell
# Health check (default)
.\quick-start.ps1

# Start backend only
.\quick-start.ps1 -Backend

# Start frontend only
.\quick-start.ps1 -Frontend

# Run tests
.\quick-start.ps1 -Test
```

### 🔍 `verify-stack.ps1` - Comprehensive Verification
Detailed verification script to check all components and dependencies.

```powershell
# Basic verification
.\verify-stack.ps1

# Detailed output
.\verify-stack.ps1 -Detailed

# Auto-fix common issues
.\verify-stack.ps1 -FixIssues
```

**Checks:**
- Python and Node.js installation
- Project structure integrity
- Dependency installation
- Backend API functionality
- Frontend build process
- Integration components

### 🔄 `rebuilt-env.ps1` - Environment Setup
Sets up Python virtual environment and installs dependencies.

```powershell
.\rebuilt-env.ps1
```

## Quick Start Guide

1. **First Time Setup:**
   ```powershell
   # Setup environment and dependencies
   .\rebuilt-env.ps1
   
   # Verify everything is working
   .\verify-stack.ps1 -Detailed
   ```

2. **Development:**
   ```powershell
   # Start full stack for development
   .\run-full-stack.ps1
   ```

3. **Testing:**
   ```powershell
   # Quick health check
   .\quick-start.ps1
   
   # Run comprehensive tests
   .\quick-start.ps1 -Test
   ```

## Service URLs

- **Backend API:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Port Already in Use:**
   - Scripts automatically detect and use alternative ports
   - Check output for actual ports being used

2. **Dependencies Missing:**
   ```powershell
   .\verify-stack.ps1 -FixIssues
   ```

3. **Virtual Environment Issues:**
   ```powershell
   # Remove and recreate environment
   Remove-Item -Recurse -Force .venv
   .\rebuilt-env.ps1
   ```

4. **Node.js Dependencies:**
   ```powershell
   cd web-ui
   npm install
   cd ..
   ```

### Manual Verification

If scripts fail, you can manually check:

1. **Backend:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Frontend:**
   ```powershell
   cd web-ui
   npm start
   ```

## Script Features

### Error Handling
- Graceful error handling and reporting
- Automatic cleanup on exit
- Port conflict resolution
- Dependency checking

### Development Features
- Auto-reload for backend changes
- Hot reload for frontend changes
- Comprehensive logging
- Health monitoring

### Production Features
- Optimized builds
- Multi-worker backend
- Static file serving
- Environment variable management

## Requirements

- **Python 3.10+** with pip
- **Node.js 16+** with npm
- **PowerShell 5.0+** (Windows)
- **Git** (for development)

## Architecture

```
Enhanced Purview CLI v2.0
├── Backend (FastAPI)
│   ├── API Routes (/api/v1/*)
│   ├── WebSocket (/ws)
│   ├── Documentation (/docs, /redoc)
│   └── Health Check (/health)
├── Frontend (React + TypeScript)
│   ├── Material-UI Components
│   ├── Redux Store
│   ├── WebSocket Integration
│   └── API Service Layer
└── Integration
    ├── Shared Models
    ├── Authentication
    └── Real-time Updates
```

---

For more information, see the main project documentation.
