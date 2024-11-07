from fastapi import FastAPI
from pydantic import BaseModel, PositiveInt
from fastapi.responses import JSONResponse


# Classes
class User(BaseModel):
    name: str
    age: PositiveInt
    gender: str
    length: PositiveInt

# Databases
users_db = [{"name": "Pietje", "age": 20, "gender": "M", "length": 182},{"name": "Hendrik", "age": 21, "gender": "M", "length": 190}]

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/users")
def read_users():
    return JSONResponse(content=users_db)

@app.get("/users/{user_id}")
def read_user(user_id: int):
    return JSONResponse(content=users_db[user_id])