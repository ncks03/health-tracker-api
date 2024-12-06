
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, APIRouter, HTTPException
from typing import Optional
from schemas.dtos import GymDTO
from models.entities import Gym, Customer
from schemas.responses import GymResponse
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
                gyms_strucured = {"gyms":[
                    GymResponse(
                        id=gym.id,
                        name=gym.name,
                        address_place=gym.address_place
                    )
                    for gym in all_gyms
                ]}

                return gyms_strucured
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

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"an error occurred during search{e}")

@router.post("/")
async def create_gym(gym: GymDTO, db = Depends(get_db)):
    try:
        gym= Gym(
            name=gym.name,
            address_place=gym.address_place
        ) # Create db entity from data
        db.add(gym) # Add entity to database
        db.commit() # Commit changes
        db.refresh(gym) # Refresh database
        return gym
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"an error occurred {e}")

@router.get("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(Gym).filter(Gym.id == gym_id).first()

        if gym is None:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")

        return gym

    # Only catch SQLAlchemy errors here
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Server error occurred during search")

@router.delete("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(Gym).filter(Gym.id == gym_id).first()

        if gym is None:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")

        db.delete(gym)
        db.commit()
        return {"message": f"Gym with id {gym_id} successfully deleted"}

    # Only catch SQLAlchemy errors here
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Server error occurred during search")


@router.get("/{gym_id}/customers")
async def get_customers_by_gym_id(gym_id: int, db = Depends(get_db)):
    try:
        customers = db.query(Customer).filter(Customer.gym_id == gym_id).all()
        # check if the customers variable empty
        if not customers:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} has no customers")

        return customers
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Server error occurred during search")