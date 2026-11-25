# Start Full Stack Application

This guide explains how to run both backend and frontend together.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase project credentials
- Git (optional)

## Quick Start (Two Terminals)

### Terminal 1: Start Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Started server process [xxxx]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Backend is ready at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Terminal 2: Start Frontend

```powershell
cd frontend
npm install  # Only needed first time
npm run dev
```

Expected output:
```
  VITE v8.3.8  ready in XXXX ms
  ➜  Local:   http://localhost:5173/
```

Frontend is ready at: http://localhost:5173

## Full URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/v1/docs |
| ReDoc | http://localhost:8000/api/v1/redoc |
| Health Check | http://localhost:8000/health |

## First Time Setup

### 1. Configure Backend Environment
```powershell
cd backend
# Create .env file with your Supabase credentials
# See backend/.env.example for template
```

### 2. Configure Frontend Environment
```powershell
cd frontend
# Create .env file with Supabase credentials
# See frontend/.env.example for template
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
```

## Testing the Connection

1. Open browser to http://localhost:5173
2. Create account or login
3. Navigate through pages
4. Create a hobby, skill, or goal
5. Check backend logs for API calls

## Stopping Services

Press `CTRL+C` in each terminal to stop the services.

## Troubleshooting

### Backend won't start
- Check if port 8000 is in use: `netstat -ano | findstr :8000`
- Verify Python installation: `python --version`
- Check .env file exists and has DATABASE_URL

### Frontend won't start
- Check if port 5173 is in use: `netstat -ano | findstr :5173`
- Verify Node.js: `node --version`
- Clear node_modules: `rm -r node_modules` then `npm install`

### Can't connect frontend to backend
- Verify backend is running (check terminal 1)
- Check VITE_API_BASE_URL in frontend/.env is `http://localhost:8000`
- Check browser console for CORS errors

### Auth not working
- Verify Supabase credentials in both .env files
- Check browser local storage for auth token
- Try signing up instead of signing in

## Development Workflow

1. **Backend changes:** Automatically reloads with `--reload` flag
2. **Frontend changes:** Hot reload enabled in Vite
3. **Database changes:** Restart backend to pick up schema changes

## Production Deployment

See deployment guides:
- Backend: `backend/README.md`
- Frontend: `frontend/GETTING_STARTED.md`

## Commands Reference

### Backend
```powershell
cd backend
python -m uvicorn app.main:app --reload           # Dev mode
python -m uvicorn app.main:app --host 0.0.0.0    # Production
pytest                                              # Run tests
```

### Frontend
```powershell
cd frontend
npm run dev              # Development
npm run build           # Production build
npm run preview         # Preview build
npm run test            # Run tests
npm run test:watch      # Watch mode
npm run lint            # Check code
```

## Architecture Overview

```
User Browser (http://localhost:5173)
        ↓
   React Frontend
        ↓ (HTTP + JWT)
 FastAPI Backend (http://localhost:8000)
        ↓
 Supabase PostgreSQL
```

## Support

- **Frontend Issues:** See `frontend/GETTING_STARTED.md`
- **Backend Issues:** See `backend/README.md` (if exists)
- **Database Issues:** See `docs/database-schema.md`
- **Supabase Docs:** https://supabase.com/docs
