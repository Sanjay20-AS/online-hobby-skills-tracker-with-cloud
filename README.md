# Online Hobby & Skills Tracker with Community Sharing

A cloud-native platform for tracking personal hobbies and skills, with community sharing features.

> **Development Stage:** Phase 6 — Complete Frontend Implementation ✅
> 
> Backend Phase 5: 23 endpoints, real database, JWT auth ✅
> Frontend Phase 6: 12 pages, authentication, full API integration ✅

---

## ⚠️ Security Warning

**Never commit real credentials, API keys, or secrets to this repository.**

- Keep `.env` files local only.
- Only `.env.example` files (with placeholder values) are tracked by Git.
- Never put Supabase service-role keys in frontend variables.

---

## Technology Stack

| Layer              | Technology                     |
|--------------------|--------------------------------|
| Frontend           | React 19 + Vite 8 (JavaScript) |
| Backend            | Python 3.11 + FastAPI          |
| Authentication     | Supabase Auth                  |
| Database           | Supabase PostgreSQL            |
| Cloud Storage      | Supabase Storage               |
| Frontend Hosting   | Vercel                         |
| Backend Hosting    | Render                         |
| Version Control    | GitHub                         |
| CI/CD              | GitHub Actions                 |
| Local Development  | Docker + Supabase CLI          |

---

## Prerequisites (Windows 11)

Install the following before getting started:

| Tool | Minimum Version | Download |
|------|----------------|---------|
| Node.js (LTS) | v18+ | https://nodejs.org |
| Python | 3.11+ | https://python.org |
| Git | 2.x | https://git-scm.com |
| Docker Desktop | 4.x | https://docs.docker.com/desktop/windows/ |
| Supabase CLI | latest | https://supabase.com/docs/guides/cli |

> **Supabase CLI** is not currently installed on this machine. It can be installed later when local Supabase development is needed. Install via:
> ```powershell
> winget install Supabase.CLI
> ```

---

## Project Structure

```
(workspace root)/
├── frontend/          # React + Vite application
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── contexts/
│       ├── hooks/
│       ├── layouts/
│       ├── pages/
│       ├── services/
│       └── utils/
├── backend/           # Python FastAPI application
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── supabase/          # Database migrations
├── docs/              # Project documentation
├── scripts/           # Utility scripts
└── .github/workflows/ # CI/CD pipelines
```

---

## Frontend Setup

### 1. Navigate to the frontend directory

```powershell
cd frontend
```

### 2. Install dependencies

```powershell
npm install
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
# Edit .env and fill in your Supabase project values
```

### 4. Start the development server

```powershell
npm run dev
```

The app will be available at http://localhost:5173

### Other frontend commands

```powershell
npm run build       # Production build
npm run preview     # Preview production build locally
npm run test        # Run tests once
npm run test:watch  # Run tests in watch mode
```

---

## Backend Setup

### 1. Navigate to the backend directory

```powershell
cd backend
```

### 2. Create the Python virtual environment (first time only)

```powershell
py -3.11 -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

> **PowerShell Execution Policy:** If you see a script execution error, run this once in an elevated PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure environment

```powershell
Copy-Item .env.example .env
# Edit .env and fill in your database and Supabase values
```

### 6. Start the development server

```powershell
python -m uvicorn app.main:app --reload --app-dir .
```

The API will be available at:
- Base URL: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/api/v1/docs

---

## Environment Files

Both `frontend/.env.example` and `backend/.env.example` contain the required variable names with placeholder values.

Copy each to `.env` in its respective directory and fill in your actual values.

**Frontend variables** (`frontend/.env`):

```
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=YOUR_SUPABASE_PROJECT_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY
```

**Backend variables** (`backend/.env`):

```
APP_ENV=development
APP_NAME=Online Hobby and Skills Tracker
API_V1_PREFIX=/api/v1
DATABASE_URL=YOUR_DATABASE_CONNECTION_STRING
SUPABASE_URL=YOUR_SUPABASE_PROJECT_URL
SUPABASE_ANON_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY
CORS_ORIGINS=http://localhost:5173
```

---

## Git Security

The `.gitignore` excludes:

- All `.env` files (real credentials)
- `backend/.venv/` (Python virtual environment)
- `frontend/node_modules/` (npm packages)
- `frontend/dist/` (build output)
- Python `__pycache__` and compiled files
- IDE and OS-specific files

Only `.env.example` files are committed to Git.
