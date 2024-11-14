### Dependencies ###
import psycopg2
import os
from dotenv import load_dotenv
from fastapi import FastAPI

### Imports ###
from functions import calculate_age
from entities import *
import dtos

# Load environment variables
### DO NOT PUSH .ENV TO GIT ###
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME") #Insert username variable name here
DB_PASSWORD = os.getenv("DB_PASSWORD") #Insert password variable name here

# Connection to postgresql Database
db_connection = psycopg2.connect(
    database="health-app-db",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host="localhost",  # IP Adress of DB host
    port="5432"  # Standard host port
)

# API Initialisation
app = FastAPI()

# Endpoints definition
@app.get("/users")
def get_data_from_db():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM customers")
    data = cursor.fetchall()
    cursor.close()
    return {"data": data}

@app.post("/users")
def create_user(customer: CustomerDTO):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO public.users (name, birth_date, gender, length) VALUES (user[name], user[birth_date], user[gender], user[length])")
