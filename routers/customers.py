from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import date

from schemas.dtos import CustomerDTO, ProgressDTO, GoalDTO, CustomerUpdateDTO
from schemas.responses import CustomerResponse, CustomerProgressResponse, CustomerGoalResponse, SingleCustomerResponse
from models.entities import Customer as CustomerTable
from models.entities import Goal as GoalsTable
from models.entities import Progress as ProgressTable
from services.functions import get_db, violates_constraint, calculate_age, calculate_daily_calories, \
    get_data_from_db_to_calculate, calculate_daily_calories_and_macros, calculate_daily_calories_all_customers

# Define router endpoint
router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

### GET REQUESTS ###

@router.get("/")
async def get_customer_by_name(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        db = Depends(get_db)
): # (;
    try:
        # Define sqlalchemy statement
        if first_name and last_name:
            # If both first name and last name are given
            first_name = first_name.capitalize()
            last_name = last_name.capitalize()
            statement = (
                select(CustomerTable)
                .where(CustomerTable.first_name==first_name)
                .where(CustomerTable.last_name==last_name)
            )
        elif first_name: # If only first name is given
            first_name = first_name.capitalize()
            statement = (
                select(CustomerTable)
                .where(CustomerTable.first_name==first_name)
            )
        elif last_name: # if only last name is given
            last_name = last_name.capitalize()
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

        # Return data dictionary
        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}")
async def get_customer_by_id(customer_id: int, db = Depends(get_db)):
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
            current_weight = 0

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

        return response

    except HTTPException as e:
        raise e

    except Exception as e: #Raise exception for invalid ids
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/goals")
async def get_customer_goals(customer_id: int, db = Depends(get_db)):
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

    except HTTPException as e:
        raise e

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/progress")
async def get_customer_progress(customer_id: int, db = Depends(get_db)):
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

    except HTTPException as e:
        raise e

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/progress/recent")
async def get_customer_progress_by_id(customer_id: int, db = Depends(get_db)):
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

    except HTTPException as e:
        raise e

    except Exception as e:  # Raise exception for invalid ids
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.get("/{customer_id}/daily_calorie_intake")
async def get_daily_calorie_intake(customer_id: int,
                                   from_start_date: Optional[bool] = False,
                                   db = Depends(get_db)):
    try:
        customer_data = get_data_from_db_to_calculate(customer_id, db)

        if not customer_data:
            raise HTTPException(
                status_code=404,
                detail=f"the customer with id {customer_id} does not exist or is missing essential data"
            )

        if from_start_date:
            deadline_in_days = (customer_data["end_date"] - customer_data["start_date"]).days
        else:
            deadline_in_days =  (customer_data["end_date"] - customer_data["date"]).days

        detailed_daily_cal_intake = calculate_daily_calories_and_macros(
            customer_data["weight"],
            customer_data["weight_goal"],
            deadline_in_days,
            customer_data["length"],
            calculate_age(customer_data["birth_date"]),
            customer_data["gender"],
            customer_data["activity_level"]
        )

        response_data = {"customer_data": customer_data,
                         "detailed_daily_cal_intake": detailed_daily_cal_intake}


        if detailed_daily_cal_intake["total_daily_calories"] < 1200:
            response_data["realism"] = False
            response_data["message"] = (f"the expected weight loss before the deadline is unrealistic "
                                        f"and results a calorie intake less than 1200 per day!")
        else:
            response_data["realism"] = True

        return response_data

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

### POST REQUESTS ###
@router.post("/")
async def create_customer(customer: CustomerDTO, db = Depends(get_db)):
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

        user_exists = db.query(CustomerTable).filter(
            CustomerTable.gym_id == customer.gym_id,
            CustomerTable.first_name == customer.first_name,
            CustomerTable.last_name == customer.last_name,
            CustomerTable.birth_date == customer.birth_date,
            CustomerTable.gender == customer.gender,
            CustomerTable.length == customer.length,
            CustomerTable.activity_level == customer.activity_level
        ).first()

        if user_exists:
            raise HTTPException(
                status_code=400,
                detail=f"This user already exists!"
            )

        if customer.activity_level:
            if violates_constraint(customer.activity_level):
                raise HTTPException(
                    status_code=422,
                    detail=f"The activity level must be between 1.2 and 1.725."
                )
        if customer.gender:
            genders = ["male", "female"]
            if customer.gender not in genders:
                raise HTTPException(
                    status_code=422,
                    detail=f"The gender must be 'male' or 'female'."
                )

        db.add(customer) # Add entity to database
        db.commit() # Commit changes
        db.refresh(customer) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message":f"Customer {customer.first_name} {customer.last_name} successfully added."}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.post("/{customer_id}/progress")
async def create_progress_for_customer(customer_id: int, progress: ProgressDTO, db = Depends(get_db)):
    try:
        customer = db.query(CustomerTable).filter(CustomerTable.id==customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail=f"No customer with id {customer_id}")

        progress = ProgressTable(
            customer_id=customer_id,
            date=date.today(),
            weight=progress.weight
        ) # Create db entity from data

        if progress.weight <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"Weight must be greater than 0."
            )
        else:
            db.add(progress) # Add entity to database
            db.commit() # Commit changes
            db.refresh(progress) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message": f"Progress successfully saved."}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

@router.post("/{customer_id}/goals")
async def create_goal_for_customer(customer_id: int, goal: GoalDTO, db = Depends(get_db)):
    try:
        goal = GoalsTable(
            customer_id=customer_id,
            weight_goal=goal.weight_goal,
            start_date=goal.start_date,
            end_date=goal.end_date
        ) # Create db entity from data

        if goal.start_date == goal.end_date:
            raise HTTPException(
                status_code=400,
                detail=f"Start date and end date cannot be the same"
            )
        elif goal.end_date < goal.start_date:
            raise HTTPException(
                status_code=400,
                detail=f"End date cannot be before start date"
            )
        elif goal.end_date <= date.today():
            raise HTTPException(
                status_code=400,
                detail=f"End date must be in the future"
            )
        else:
            db.add(goal) # Add entity to database
            db.commit() # Commit changes
            db.refresh(goal) # Refresh database

            return JSONResponse(
                status_code=201,
                content={"message": f"Goal successfully added."}
            )

    # Raise error for http exception
    except HTTPException as e:
        raise e

    # Raise other errors
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

### PATCH REQUESTS ###

# Is deze wel nodig? waarom zou je deze gegevens willen veranderen?
@router.patch("/{customer_id}")
async def update_customer(customer_id, data: CustomerUpdateDTO, db = Depends(get_db)):
    try:
        customer = db.query(CustomerTable).filter(CustomerTable.id==customer_id).first()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"No customer with id {customer_id}"
            )

        if data.activity_level:
            if violates_constraint(data.activity_level):
                raise HTTPException(
                    status_code=422,
                    detail=f"The activity level must be between 1.2 and 1.725."
                )

        customer_dict = data.dict(exclude_unset=True)

        for key, value in customer_dict.items():
            setattr(customer, key, value)

        db.commit() # Commit changes
        db.refresh(customer) # Refresh database

        return JSONResponse(
            status_code=200,
            content={"message":f"Customer {customer.first_name} {customer.last_name} successfully updated."}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )

### DELETE REQUESTS ###

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db = Depends(get_db)):
    try:
        customer = db.query(CustomerTable).filter(CustomerTable.id == customer_id).first()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} does not exist."
            )

        db.delete(customer)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"message": f"Customer with id {customer_id} successfully deleted."}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {e}"
        )