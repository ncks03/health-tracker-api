### Dependencies ###
# import psycopg2
import os
from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

### Imports ###
from .routers import customers
from functions import calculate_age
from entities.entities import Customer as CustomerEntity
from entities.entities import Gym as GymEntity
from entities.entities import Progress as ProgressEntity
from entities.entities import Goal as GoalEntity
from dtos.dtos import CustomerDTO, GymDTO, ProgressDTO, GoalDTO

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

@app.post("/progress")
def create_user(customer: CustomerDTO, db = Depends(get_db)):
    customer= CustomerEntity(**customer.dict()) # Create db entity from data
    db.add(customer) # Add entity to database
    db.commit() # Commit changes
    db.refresh(customer) # Refresh database
