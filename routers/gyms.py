import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from dtos.dtos import GymDTO
import entities.entities as entities

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

router = APIRouter(
    prefix="/gyms",
    tags=["gyms"]
)

@router.get("/")
async def read_gyms(db = Depends(get_db)):
    try:
        db.execute("SELECT * FROM gym")
    except:
        raise HTTPException(status_code=404, detail="Customer not found")

@router.post("/create_gym")
async def create_user(gym: GymDTO, db = Depends(get_db)):
    gym= entities.Gym(
        name=gym.gym_name,
        address_place=gym.address_city,
    ) # Create db entity from data
    db.add(gym) # Add entity to database
    db.commit() # Commit changes
    db.refresh(gym) # Refresh database
    return gym