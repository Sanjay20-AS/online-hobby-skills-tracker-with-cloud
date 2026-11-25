import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_dir)

from app.main import app

routes = [r.path for r in app.routes]
print("FastAPI app loaded successfully.")
print(f"App title: {app.title}")
print(f"Registered routes: {routes}")
print("Health endpoint present:", "/health" in routes)
