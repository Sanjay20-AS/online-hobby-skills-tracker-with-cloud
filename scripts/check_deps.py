#!/usr/bin/env python
"""Check key backend dependencies."""
import sys

packages = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "alembic", "supabase", "jwt"]
missing = []

for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg}")
        missing.append(pkg)

if missing:
    print(f"\nMissing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✅ All key packages present")
    sys.exit(0)
