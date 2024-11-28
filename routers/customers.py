import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import date

from schemas.dtos import CustomerDTO, ProgressDTO, GoalDTO
from schemas.responses import CustomerResponse, CustomerProgressResponse, CustomerGoalResponse, SingleCustomerResponse
from models.entities import Customer as CustomerTable
from models.entities import Goal as GoalsTable
from models.entities import Progress as ProgressTable

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
async def read_customer_by_name(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        db = Depends(get_db)
): # (;
    try:
        # Define sqlalchemy statement
        if first_name and last_name: # If both first name and last name are given
            statement = (
                select(CustomerTable)
                .where(CustomerTable.first_name==first_name)
                .where(CustomerTable.last_name==last_name)
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

        # Check if customer is found in database
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No customers found for name "
                       f"{first_name if first_name else ""} "
                       f"{last_name if last_name else ""}"
            )

        # Convert response to response model
        response = [
            CustomerResponse(
                id = x.id,
                first_name=x.first_name,
                last_name=x.last_name,
                birth_date=x.birth_date,
                gender=x.gender,
                length=x.length,
                gym_id=x.gym_id,
                activity_level=x.activity_level
            )
            for x in result
        ]

        # Store result in data dict
        data = {
            "customers": response
        }

        # Return data dictionary
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

        current_weight=(db.query(ProgressTable.weight)
                        .filter(ProgressTable.customer_id == customer_id)
                        .order_by(ProgressTable.date)
                        .limit(1).scalar()
                        )

        if not current_weight:
            current_weight = "No progress logged"

        # Convert response to response model
        response = SingleCustomerResponse(
                id = result.id,
                first_name=result.first_name,
                last_name=result.last_name,
                birth_date=result.birth_date,
                gender=result.gender,
                length=result.length,
                weight=current_weight,
                gym_id=result.gym_id,
                activity_level=result.activity_level
            )

        # Store result in data dict
        data = {
            "data": response
        }

        return data

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

        # Define results in goal response model
        response = [
            CustomerGoalResponse(
            id=x.id,
            weight_goal=x.weight_goal,
            start_date=x.start_date,
            end_date=x.end_date)
            for x in result
        ]

        # Get customer details from database
        customer_details = db.query(CustomerTable).filter(CustomerTable.id==customer_id).first()

        # Store results in data dict
        data={
            "customer_id": customer_id,
            "customer_name": customer_details.first_name + " " + customer_details.last_name,
            "goals": response
        }

        # Return JSON Response
        return data


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

        # Define results in goal response model
        response = [
            CustomerProgressResponse(
                date=x.date,
                weight=x.weight,
            )
            for x in result
        ]

        # Get customer details from database
        customer_details = db.query(CustomerTable).filter(CustomerTable.id == customer_id).first()

        # Store results in data dict
        data = {
            "customer_id": customer_id,
            "customer_name": customer_details.first_name + " " + customer_details.last_name,
            "progress": response
        }

        # Return JSON Response
        return data

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

        # Define results in goal response model
        response = CustomerProgressResponse(
                date=result.date,
                weight=result.weight,
            )

        # Get customer details from database
        customer_details = db.query(CustomerTable).filter(CustomerTable.id == customer_id).first()

        # Store results in data dict
        data = {
            "customer_id": customer_id,
            "customer_name": customer_details.first_name + " " + customer_details.last_name,
            "progress": response
        }

        # Return JSON Response
        return data

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=404,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/daily_calorie_intake")
async def get_daily_calorie_intake(customer_id, db = Depends(get_db)):
    # Algorithm goes here
    return "This function does not work yet"

### POST REQUESTS ###
@router.post("/")
async def create_user(customer: CustomerDTO, db = Depends(get_db)):
    try:
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

        return JSONResponse(
            status_code=201,
            content={"message":f"Customer {customer.first_name} {customer.last_name} successfully added."}
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )

@router.post("/{customer_id}/progress")
async def create_progress_for_user(customer_id: int, progress: ProgressDTO, db = Depends(get_db)):
    try:
        customer = db.query(CustomerTable).filter(CustomerTable.id==customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail=f"No customer with id {customer_id}")

        progress = ProgressTable(
            customer_id=customer_id,
            date=date.today(),
            weight=progress.weight
        ) # Create db entity from data
        db.add(progress) # Add entity to database
        db.commit() # Commit changes
        db.refresh(progress) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message": f"Progress successfully saved."}
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )

@router.post("/{customer_id}/goals")
async def create_goal_for_user(customer_id: int, goal: GoalDTO, db = Depends(get_db)):
    try:
        goal = GoalsTable(
            customer_id=customer_id,
            weight_goal=goal.weight_goal,
            start_date=goal.start_date,
            end_date=goal.end_date
        ) # Create db entity from data
        db.add(goal) # Add entity to database
        db.commit() # Commit changes
        db.refresh(goal) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message": f"Goal successfully added."}
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )

### PATCH REQUESTS ###

@router.patch("/{customer_id}")
async def update_customer(customer: CustomerDTO, db = Depends(get_db)):
    try:
        customer = CustomerTable(
            customer_id=customer.id,
            gym_id=customer.gym_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            birth_date=customer.birth_date,
            gender=customer.gender,
            length=customer.length,
            activity_level=customer.activity_level
        ) # Create db entity from data
        db.update(CustomerTable).values(customer) # Add entity to database
        db.commit() # Commit changes
        db.refresh(customer) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message":f"Customer {customer.first_name} {customer.last_name} successfully updated."}
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )

### DELETE REQUESTS ###

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db = Depends(get_db)):
    try:
        customer = db.query(CustomerTable).filter(CustomerTable.id == customer_id).first()

        db.delete(customer)
        db.commit()
        return JSONResponse(
            status_code=200,
            content={"message": f"Customer with id {customer_id} successfully deleted."}
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )