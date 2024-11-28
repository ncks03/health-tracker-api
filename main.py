### Dependencies ###
import os

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

### Imports ###
from routers import customers, gyms, goals, progress

# Load environment variables
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

def run_migrations():
    """
    Run Alembic migrations.
    """
    # Maak een configuratie object voor alembic en laad de configuratie
    alembic_cfg = Config("alembic.ini")

    # Stel de sqlalchemy.url optie in de configuratie
    alembic_cfg.set_main_option("sqlalchemy.url", DB_URL)

    # Voer de upgrade uit
    command.upgrade(alembic_cfg, "head")

run_migrations()

# API Initialisation
app = FastAPI()
app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
