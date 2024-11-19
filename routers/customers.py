import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from dtos.dtos import CustomerDTO, GoalDTO
import entities.entities as entities
from entities.entities import Customer as CustomerTable
from entities.entities import Goal as GoalsTable

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

@router.get("/")
async def read_customers(db = Depends(get_db)):
    try:
        result = db.query(CustomerTable).order_by(entities.Customer.id)
        return result.all()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
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
            .join(CustomerTable.first_name)
            .where(GoalsTable.customer_id==customer_id)
            .order_by(GoalsTable.start_date)
        )
        # Execute statement and store result
        result = db.execute(statement).scalars().all()

        result_json = jsonable_encoder(result, sqlalchemy_safe=True)

        data={
            "customer_id": customer_id,
            "customer_name": result_json["first_name"],
            "data": result_json
        }

        return JSONResponse(
            status_code=200,
            content=data
        )

    except TypeError: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"No goals found for customer with id {customer_id}"
        )

@router.get("/{customer_id}/progress")
async def read_customer_progress(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(CustomerTable)
            .where(CustomerTable.id==customer_id)
        )
        # Execute statement and store result
        result = db.execute(statement).first()
        # Store result in data dict
        data = {
            "data": list(result)
        }
        return data

    except TypeError: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {customer_id} not found"
        )

@router.get("/{customer_id}/progress/{progress_id}")
async def customer_progress_by_id(customer_id: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(CustomerTable)
            .where(CustomerTable.id==customer_id)
        )
        # Execute statement and store result
        result = db.execute(statement).first()
        # Store result in data dict
        data = {
            "data": list(result)
        }
        return data

    except TypeError: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {customer_id} not found"
        )

@router.get("/")
async def read_customer_by_name(customer_name: int, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(CustomerTable)
            .where(CustomerTable.first_name==customer_name)
        )
        # Execute statement and store result
        result = db.execute(statement).all()
        # Store result in data dict
        data = {
            "data": list(result)
        }
        return data

    except TypeError: #Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {customer_id} not found"
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