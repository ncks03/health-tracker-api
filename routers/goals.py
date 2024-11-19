import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from dtos.dtos import GoalDTO
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
    prefix="/goals",
    tags=["goals"]
)

@router.get("/")
async def read_goals(db = Depends(get_db)):
    try:
        db.execute("SELECT * FROM goals")
    except:
        raise HTTPException(status_code=404, detail="Customer not found")

@router.post("/create_goal")
async def create_user(goal: GoalDTO, db = Depends(get_db)):
    goal = entities.Goal(
        customer_id = goal.customer_id,
        weight_goal = goal.weight_goal,
        start_date = goal.start_date,
        end_date = goal.end_date,
    ) # Create db entity from data
    db.add(goal) # Add entity to database
    db.commit() # Commit changes
    db.refresh(goal) # Refresh database
    return f"Goal successfully created"