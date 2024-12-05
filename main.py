### Dependencies ###
import os

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

### Imports ###
from routers import customers, gyms, goals, progress

# API Initialisation
app = FastAPI()

@app.get("/")
def read_root():
    return "the server is up and running"
app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
