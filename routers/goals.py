import os
from asyncio import start_server

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

from schemas.dtos import GoalDTO
from schemas.responses import GoalResponse
from models.entities import Goal as GoalsTable

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
async def read_goals(
    start_date: str = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    db=Depends(get_db)
):
    """
    Fetch all goals. Optionally filter by end_date or start_date.
    """
    try:
        query = db.query(GoalsTable)

        if end_date:
            query = query.filter(GoalsTable.end_date == end_date)
        if start_date:
            query = query.filter(GoalsTable.start_date == start_date)

        return query.order_by(GoalsTable.id).all()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Could not get goals: {e}"
        )

@router.post("/")
async def create_goal(goal: GoalDTO, db = Depends(get_db)):
    try:
        goal = GoalsTable(
            customer_id = goal.customer_id,
            weight_goal = goal.weight_goal,
            start_date = goal.start_date,
            end_date = goal.end_date,
        ) # Create db entity from data
        db.add(goal) # Add entity to database
        db.commit() # Commit changes
        db.refresh(goal) # Refresh database

        return JSONResponse(
            status_code=201,
            content= {"message":f"Added goal with end date: {goal.end_date} for customer with id: {goal.customer_id}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Could not add new goal: {e}"
        )

@router.get("/{goals_id}", response_model=GoalResponse)
async def get_goal_by_id(goals_id: int, db=Depends(get_db)):
    """
    Fetch a specific goal by its ID.
    """
    try:
        goal = db.query(GoalsTable).filter(GoalsTable.id == goals_id).first()

        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goals_id} not found."
            )

        return goal

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve goal with ID {goals_id}: {e}"
        )
