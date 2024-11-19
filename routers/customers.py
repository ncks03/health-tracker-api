import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional

from dtos.dtos import CustomerDTO, GoalDTO
import entities.entities as entities
from entities.entities import Customer as CustomerTable
from entities.entities import Goal as GoalsTable
from entities.entities import Progress as ProgressTable

# Load environment variables
### DO NOT PUSH .ENV TO GIT ###
load_dotenv()

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

# Define router endpoint
router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

### GET REQUESTS ###

# @router.get("/")
# async def read_customers(db = Depends(get_db)):
#     try:
#         result = db.query(CustomerTable).order_by(entities.Customer.id)
#         return result.all()
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )
@router.get("/") #ISSUE: All entries with either last name or first name are returned, and not if only both are equal
async def read_customer_by_name(first_name: Optional[str] = None, last_name: Optional[str] = None, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        if first_name and last_name: # If both first name and last name are given
            statement = (
                select(CustomerTable)
                .where(CustomerTable.first_name==first_name
                       and CustomerTable.last_name==last_name)
            )
        elif first_name: # If only first name is given
            statement = (
                select(CustomerTable)
                .where(CustomerTable.first_name==first_name)
            )
        elif last_name: # if only last name is given
            statement = (
                select(CustomerTable)
                .where(CustomerTable.last_name==last_name)
            )
        else: # If no names where given
            statement = (
                select(CustomerTable)
            )

        # Execute statement and store result
        result = db.execute(statement).scalars().all()

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No customers found for name "
                       f"{first_name if first_name else ""} "
                       f"{last_name if last_name else ""}"
            )

        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        # Store result in data dict
        data = {
            "data": result_json
        }

        return data

    except Exception as e: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}")
async def read_customer_by_id(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(CustomerTable)
            .where(CustomerTable.id==customer_id)
        )
        # Execute statement and store result
        result = db.execute(statement).scalars().first()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        # Store result in data dict
        data = {
            "data": result_json
        }

        return JSONResponse(
            status_code=200,
            content=data
        )

    except Exception as e: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/goals")
async def read_customer_goals(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(GoalsTable)
            .where(GoalsTable.customer_id==customer_id)
            .order_by(GoalsTable.start_date)
        )
        # Execute statement and store result
        result = db.execute(statement).scalars().all()

        # Check if user has any goals
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No goals found for customer with id {customer_id}"
            )

        # Convert results to JSON readable format
        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        # Store results in data dict
        data={
            "customer_id": customer_id,
            "data": result_json
        }

        # Return JSON Response
        return JSONResponse(
            status_code=200,
            content=data
        )


    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/progress")
async def read_customer_progress(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(ProgressTable)
            .where(ProgressTable.customer_id==customer_id)
        )
        # Execute statement and store result
        result = db.execute(statement).scalars().all()

        # Check if user has progress saved
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No progress found for customer with id {customer_id}"
            )

        # Convert results to json readable format
        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        # Store result in data dict
        data = {
            "data": result_json
        }

        # Return JSON Response
        return JSONResponse(
            status_code=200,
            content=data
        )

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/progress/recent")
async def customer_progress_by_id(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(ProgressTable)
            .where(ProgressTable.customer_id == customer_id)
            .order_by(ProgressTable.date)
            .limit(1)
        )

        # Execute statement and store result
        result = db.execute(statement).scalars().first()

        # Check if user has progress saved
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No progress found for customer with id {customer_id}"
            )

        # Convert results to json readable format
        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        # Store result in data dict
        data = {
            "data": result_json
        }

        # Return JSON Response
        return JSONResponse(
            status_code=200,
            content=data
        )

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/daily_calorie_intake")
async def get_daily_calorie_intake(customer_id, db = Depends(get_db)):
    pass

### POST REQUESTS ###
@router.post("/")
async def create_user(customer: CustomerDTO, db = Depends(get_db)):
    customer = CustomerTable(
        gym_id=customer.gym_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        birth_date=customer.birth_date,
        gender=customer.gender,
        length=customer.length,
        activity_level=customer.activity_level
    ) # Create db entity from data
    db.add(customer) # Add entity to database
    db.commit() # Commit changes
    db.refresh(customer) # Refresh database
    return customer

@router.post("/")
async def create_progress_for_user(progress: ProgressDTO, db = Depends(get_db)):
    progress = ProgressTable(
        gym_id=customer.gym_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        birth_date=customer.birth_date,
        gender=customer.gender,
        length=customer.length,
        activity_level=customer.activity_level
    ) # Create db entity from data
    db.add(customer) # Add entity to database
    db.commit() # Commit changes
    db.refresh(customer) # Refresh database
    return customer

@router.post("/")
async def create_goal_for_user(goal: GoalDTO, db = Depends(get_db)):
    goal = GoalTable(
        gym_id=customer.gym_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        birth_date=customer.birth_date,
        gender=customer.gender,
        length=customer.length,
        activity_level=customer.activity_level
    ) # Create db entity from data
    db.add(customer) # Add entity to database
    db.commit() # Commit changes
    db.refresh(customer) # Refresh database
    return customer