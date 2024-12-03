### Dependencies ###
import os

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

### Imports ###
from routers import customers, gyms, goals, progress

# # Load environment variables
# DB_URL = os.getenv("DB_URL")
#
# # Connection to postgresql Database
# engine = create_engine(DB_URL)
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# API Initialisation
app = FastAPI()

@app.get("/")
def read_root():
    return "the server is up and running"
app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
