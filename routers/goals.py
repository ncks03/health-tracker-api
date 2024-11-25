import os
from asyncio import start_server

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException, Query
from starlette.responses import JSONResponse

from schemas.dtos import GoalDTO
from schemas.responses import GoalResponse
from models.entities import Goal as GoalsTable
from models.entities import Customer as CustomerTable

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
    start_date: str = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    db=Depends(get_db)
):
    """
    Fetch all goals. Optionally filter by start_date or end_date.
    Includes customer details (first and last name).
    """
    try:
        # Define the base query with a join between GoalsTable and CustomerTable
        statement = (
            select(GoalsTable, CustomerTable.first_name, CustomerTable.last_name)
            .join(CustomerTable, GoalsTable.customer_id == CustomerTable.id)
        )

        # Apply filters for start_date and end_date if provided
        if start_date:
            statement = statement.where(GoalsTable.start_date == start_date)
        if end_date:
            statement = statement.where(GoalsTable.end_date == end_date)

        # Order the results by end_date
        statement = statement.order_by(GoalsTable.end_date)

        # Execute the statement and retrieve results
        result = db.execute(statement).all()

        # Check if results are empty
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No goals found matching the given criteria."
            )

        # Format the response data
        response = [
            GoalResponse(
                id=goal.id,
                customer_id=goal.customer_id,
                customer_name=f"{first_name} {last_name}",
                weight_goal=goal.weight_goal,
                start_date=goal.start_date,
                end_date=goal.end_date,
            )
            for goal, first_name, last_name in result  # Unpack the 'result' tuple
        ]

        # Return the formatted response
        return response

    except Exception as e:
        # Raise a detailed HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Could not fetch goals: {e}"
        )

@router.get("/{goals_id}", response_model=GoalResponse)
async def get_goal_by_id(goals_id: int, db=Depends(get_db)):
    """
    Fetch a specific goal by its ID.
    """
    try:
        # Define the base query with a join between GoalsTable and CustomerTable
        statement = (
            select(GoalsTable, CustomerTable.first_name, CustomerTable.last_name)
            .join(CustomerTable, GoalsTable.customer_id == CustomerTable.id)
            .where(GoalsTable.id == goals_id)
        )

        # Execute the statement and retrieve a result.
        result = db.execute(statement).first()

        print(result)

        # Check if results are empty
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goals_id} not found."
            )

        # Unpack the result
        goal, first_name, last_name = result

        # Construct the GoalResponse object
        response = GoalResponse(
            id=goal.id,
            customer_id=goal.customer_id,
            customer_name=f"{first_name} {last_name}",  # Properly combining names
            weight_goal=goal.weight_goal,
            start_date=goal.start_date,
            end_date=goal.end_date,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve goal: {e}"
        )
