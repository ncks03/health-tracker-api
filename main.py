import json
import psycopg2
import os
from dotenv import load_dotenv
from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, PositiveInt, PastDate
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connection to postgresql Database
db_connection = psycopg2.connect(
    database="health-app-db",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    host="localhost",  # IP Adress of DB host
    port="5432"  # Standard host port
)

# Classes
class User(BaseModel):
    name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt

# Functions
def calculate_age(born):
    today = date.today()
    print(today)
    birth_date = date(year=int(born[0:4]), month=int(born[5:7]), day=int(born[8:10]))
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Read users_db.json file
users_db = {
    "users":[]
}

with open("users_db.json", "r") as file:
    data = json.load(file)
    for entry in data["users"]:
        name = entry["name"]
        age = calculate_age(entry["birth_date"])
        gender = entry["gender"]
        length = entry["length"]
        users_db["users"].append({"name": name, "age": age, "gender": gender, "length": length})

# API Initialisation
app = FastAPI()

# SQL Query
@app.get("/users")
def get_data_from_db():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM customers")
    data = cursor.fetchall()
    cursor.close()
    return {"data": data}

@app.post("/users")
def create_user(user: User):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO public.users (name, birth_date, gender, length) VALUES (user[name], user[birth_date], user[gender], user[length])")