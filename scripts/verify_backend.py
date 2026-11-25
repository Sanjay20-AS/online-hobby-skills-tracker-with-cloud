import fastapi
import uvicorn
import pydantic
import sqlalchemy
import alembic
import jwt
import httpx
import psycopg
import supabase

print("All backend package imports: OK")
print(f"FastAPI:     {fastapi.__version__}")
print(f"Uvicorn:     {uvicorn.__version__}")
print(f"Pydantic:    {pydantic.__version__}")
print(f"SQLAlchemy:  {sqlalchemy.__version__}")
print(f"PyJWT:       {jwt.__version__}")
print(f"HTTPX:       {httpx.__version__}")
print(f"Psycopg:     {psycopg.__version__}")
print(f"Supabase:    {supabase.__version__}")
