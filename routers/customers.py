import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from dtos.dtos import CustomerDTO
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

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

### GET REQUESTS ###
@router.get("/")
async def read_customers(db = Depends(get_db)):
    result = db.query(CustomerTable).order_by(entities.Customer.id)
    return result.all()

@router.get("/{customer_id}")
async def read_customer_by_id(customer_id, db = Depends(get_db)):
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

@router.get("/{customer_id}/goals")
async def read_customer_goals(customer_id, db = Depends(get_db)):
    try:
        # Define sqlalchemy statement
        statement = (
            select(CustomerTable)
            .join(GoalsTable)
            .where(GoalsTable.id==customer_id)
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
            detail=f"No goals found for customer with id {customer_id}"
        )

@router.get("/{customer_id}/progress")
async def read_customer_progress(customer_id, db = Depends(get_db)):
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
async def customer_progress_by_id(customer_id, db = Depends(get_db)):
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
async def read_customer_by_name(customer_name, db = Depends(get_db)):
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

### POST REQUESTS ###
@router.post("/create_customer")
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