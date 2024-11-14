### Dependencies ###
import psycopg2
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, sessionmaker

### Imports ###
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
# db_connection = psycopg2.connect(
#     database="health-app-db",
#     user=DB_USERNAME,
#     password=DB_PASSWORD,
#     host="localhost",  # IP Adress of DB host
#     port="5432"  # Standard host port
# )

engine = create_engine(DB_URL)

session = sessionmaker(autocommit=False, autoFlush=False, bind=engine)

# API Initialisation
app = FastAPI()

# Endpoints definition
@app.get("/users")
def get_user():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM customers")
    data = cursor.fetchall()
    cursor.close()
    return {"data": data}

@app.post("/users")
def create_user(customer: CustomerDTO, db = Depends(get_db)):
    customer= CustomerEntity(**customer.dict()) # Create db entity from data
    db.add(customer) # Add entity to database
    db.commit() # Commit changes
    db.refresh(customer) # Refresh database
