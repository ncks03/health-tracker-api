import json

from datetime import date
from fastapi import FastAPI
from pydantic import BaseModel, PositiveInt
from fastapi.responses import JSONResponse

# Classes
class User(BaseModel):
    name: str
    age: PositiveInt
    gender: str
    length: PositiveInt

def calculate_age(born):
    today = date.today()
    print(today)
    birth_date = date(year=int(born[0:4]), month=int(born[5:7]), day=int(born[8:10]))
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

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

app = FastAPI()

# Get requests
@app.get("/users")
def read_users():
    return JSONResponse(content=users_db)

@app.get("/users/{user_id}")
def read_user(user_id: int):
    return JSONResponse(content=users_db["users"][user_id])

# Post requests
@app.post("/users")
def create_user(user: User):
    with open("users_db.json", "r") as f:
        data = json.load(f)

    with open("users_db.json", "w") as out_file:
        data["users"].append(user.dict())
        json.dump(data, out_file, ensure_ascii=False)

a_user={
    "name":"Henk",
    "birth_date":"1999-11-03",
    "gender":"M",
    "length":185
}
with open("users_db.json", "r") as f:
    data = json.load(f)
    print(data)

with open("users_db.json", "w") as out_file:
    data["users"].append(a_user)
    print(data)
    json.dump(data, out_file, ensure_ascii=False)