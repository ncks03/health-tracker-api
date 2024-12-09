from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from schemas.dtos import GymDTO
from models.entities import Gym, Customer
from schemas.responses import GymResponse, CustomerResponse
from services.functions import get_db

router = APIRouter(
    prefix="/gyms",
    tags=["gyms"]
)

@router.get("/")
async def get_gyms(address_place: Optional[str] = None, db = Depends(get_db)):
    try:
        if address_place is None:
            all_gyms = db.query(Gym).all()
            # check if the gyms table in database has rows
            if all_gyms:
                # make an array of gyms with certain structure
                gyms_structured = [
                    GymResponse(
                        id=gym.id,
                        name=gym.name,
                        address_place=gym.address_place
                    )
                    for gym in all_gyms
                ]

                return gyms_structured
            # if gyms db is empty
            else:
                raise HTTPException(status_code=404, detail="there are no Gyms registered in database")

        # if a city name WAS given in the request
        else:
            gyms = db.query(Gym).filter(Gym.address_place == address_place).all()

            if not gyms:
                raise HTTPException(status_code=404, detail=f"No gyms found in {address_place}")

            return [GymResponse(
                id=gym.id,
                name=gym.name,
                address_place=gym.address_place
            ) for gym in gyms]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.post("/")
async def create_gym(gym: GymDTO, db = Depends(get_db)):
    try:
        gym= Gym(
            name=gym.name,
            address_place=gym.address_place
        ) # Create db entity from data

        # Check if a gym with same values already exists
        if db.query(Gym).filter(
                Gym.address_place == gym.address_place,
                Gym.name == gym.name).first():
            raise HTTPException(status_code=400, detail=f"Gym with name '{gym.name}'"
                                                        f" in '{gym.address_place}' already exists")

        db.add(gym) # Add entity to database
        db.commit() # Commit changes
        db.refresh(gym) # Refresh database
        return JSONResponse(
            status_code=201,
            content={"message": f"Gym '{gym.name}' is successfully registered!"}
        )
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.get("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(Gym).filter(Gym.id == gym_id).first()

        if gym is None:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")

        return GymResponse(
            id=gym.id,
            name=gym.name,
            address_place=gym.address_place
        )
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(Gym).filter(Gym.id == gym_id).first()

        if gym is None:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")

        db.delete(gym)
        db.commit()

        return JSONResponse(
            status_code=200,
            content={"message": f"Gym with id {gym_id} successfully deleted."}
        )

    # Only catch SQLAlchemy errors here
    except HTTPException as e: #Raise exception for invalid ids
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.get("/{gym_id}/customers")
async def get_customers_by_gym_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(Gym).filter(Gym.id == gym_id).first()
        if not gym:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} does not exist")

        customers = db.query(Customer).filter(Customer.gym_id == gym_id).all()
        # check if the customers variable empty
        if not customers:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} has no customers")

        return {
            "gym": gym.name,
            "customers": [
                CustomerResponse(
                    id=customer.id,
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    birth_date=customer.birth_date,
                    gender=customer.gender,
                    length=customer.length,
                    gym_id=customer.gym_id,
                    activity_level=customer.activity_level
                ) for customer in customers
            ]
        }

    except HTTPException as e: #Raise exception for invalid ids
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")