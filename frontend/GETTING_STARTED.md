# Getting Started - Hobby & Skills Tracker Frontend

## Prerequisites

- Node.js 18+ installed
- Backend running at http://localhost:8000
- Supabase credentials configured in `.env`

## Quick Start

### 1. Install Dependencies
```powershell
cd frontend
npm install
```

### 2. Configure Environment
Create `.env` file (or copy `.env.example`):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### 3. Start Backend (if not already running)
```powershell
# Terminal 1
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start Frontend
```powershell
# Terminal 2
cd frontend
npm run dev
```

Application opens at **http://localhost:5173**

## Available Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Create production build |
| `npm run preview` | Preview production build locally |
| `npm run test` | Run unit tests |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:ui` | Run tests with UI |
| `npm run lint` | Check code with ESLint |

## Troubleshooting

### "Cannot connect to backend"
- Verify backend is running on port 8000
- Check VITE_API_BASE_URL in .env
- Verify CORS is configured in backend

### "Invalid Supabase credentials"
- Verify VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env
- Check credentials haven't expired
- Ensure you're using the anonymous/publishable key (not service role)

### "Module not found errors"
- Clear node_modules: `rm -r node_modules`
- Reinstall: `npm install`
- Clear Vite cache: `rm -r .vite`

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Shared UI components
│   ├── pages/           # Page components
│   ├── contexts/        # Auth context
│   ├── services/        # API client, Supabase
│   ├── layouts/         # Layout components
│   ├── utils/           # Utilities (ProtectedRoute)
│   ├── __tests__/       # Test files
│   ├── App.jsx          # Main routing
│   └── main.jsx         # Entry point
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── index.html           # HTML template
```

## Key Features

- 🔐 Supabase authentication (signup, login, password reset)
- 🎨 12 fully functional pages
- 📊 Analytics dashboard with charts
- 🏆 Hobby, skill, goal, and milestone tracking
- 👥 Community feed with posts and comments
- 🔍 Search functionality
- 📱 Responsive design (desktop, tablet, mobile)
- 🧪 Unit tests with Vitest
- ♿ Accessible UI components

## API Integration

Frontend integrates with 23 backend endpoints:
- Profiles (GET/PUT)
- Hobbies (GET/POST/PUT/DELETE)
- Skills (GET/POST)
- Goals (GET/POST)
- Practice Sessions (GET/POST)
- Milestones (GET)
- Community Posts (GET/POST)
- Likes (POST/DELETE)
- Comments (POST)
- Analytics (GET)
- Search (GET)

All endpoints require JWT authentication.

## Deployment

### Production Build
```powershell
npm run build
```
Outputs to `dist/` directory. Ready for deployment to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Any static hosting service

### Environment Variables for Production
Set these before building:
```env
VITE_API_BASE_URL=https://api.production.com
VITE_SUPABASE_URL=your_production_supabase_url
VITE_SUPABASE_ANON_KEY=your_production_anon_key
```

## Support

For issues or questions:
1. Check the [backend documentation](../backend/README.md)
2. Review the [database schema](../docs/database-schema.md)
3. Check Supabase documentation: https://supabase.com/docs
