from fastapi import FastAPI
from pydantic import BaseModel, PositiveInt
from fastapi.responses import JSONResponse
import json

# Classes
class User(BaseModel):
    name: str
    age: PositiveInt
    gender: str
    length: PositiveInt

# Define database variables
users_db = {
    "users":[]
}

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
    users_db["users"].append(user.model_dump())
