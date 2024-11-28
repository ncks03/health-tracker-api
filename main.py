### Dependencies ###
import os
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

### Imports ###
from routers import customers, gyms, goals, progress
from services.functions import run_migrations_online

# Run alembic migrations
run_migrations_online()

# Load environment variables
### DO NOT PUSH .ENV TO GIT ###
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME") #Insert username variable name here
DB_PASSWORD = os.getenv("DB_PASSWORD") #Insert password variable name here
DB_URL = os.getenv("DB_URL")

# Connection to postgresql Database
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Initialisation
app = FastAPI()
app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
