import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from dtos.dtos import GymDTO
from entities.entities import Gym

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
        return db.query(Gym).all()
    except:
        raise HTTPException(status_code=404, detail="gym not found")

@router.post("/")
async def create_gym(gym: GymDTO, db = Depends(get_db)):
    gym= Gym(
        name=gym.name,
        address_place=gym.address_place
    ) # Create db entity from data
    db.add(gym) # Add entity to database
    db.commit() # Commit changes
    db.refresh(gym) # Refresh database
    return gym


# @router.get("/{gym_id}")
# async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
#     try:
#         gym = db.query(Gym).filter(Gym.id == gym_id).first()
#
#         if gym is None:
#             raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")
#
#         return gym
#
#     # Only catch SQLAlchemy errors here
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="Server error occurred during search")