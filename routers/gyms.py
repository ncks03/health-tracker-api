import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse

from schemas.dtos import GymDTO
from models.entities import Customer as CustomerTable
from models.entities import Gym as GymTable
from services.functions import get_db

router = APIRouter(
    prefix="/gyms",
    tags=["gyms"]
)

@router.get("/")
async def read_gyms(city: str = None, db = Depends(get_db)):
    try:
        if city is None:
            return db.query(GymTable).all()

        gyms = db.query(GymTable).filter(GymTable.address_place == city).all()
        if not gyms:
            raise HTTPException(status_code=404, detail=f"No gyms found in {city}")
        return gyms

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="an error occurred during search")

@router.post("/")
async def create_gym(gym: GymDTO, db = Depends(get_db)):
    try:
        gym = GymTable(
            name=gym.name,
            address_place=gym.address_place
        ) # Create db entity from data

        gym_exists = db.query(CustomerTable).filter(
            GymTable.name == gym.name,
            GymTable.address_place == gym.address_place,
        ).first()

        if gym_exists:
            raise HTTPException(
                status_code=400,
                detail=f"This gym already exists!"
            )

        db.add(gym) # Add entity to database
        db.commit() # Commit changes
        db.refresh(gym) # Refresh database

        return JSONResponse(
            status_code=201,
            content={"message":f"Gym {gym.name} with address: {gym.address_place} successfully added."}
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"An error occurred: {e}"
        )


@router.get("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(GymTable).filter(GymTable.id == gym_id).first()

        if gym is None:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} not found")

        return gym

    # Only catch SQLAlchemy errors here
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Server error occurred during search")

@router.delete("/{gym_id}")
async def get_gym_by_id(gym_id: int, db = Depends(get_db)):
    try:
        gym = db.query(GymTable).filter(GymTable.id == gym_id).first()

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
        customers = db.query(CustomerTable).filter(CustomerTable.gym_id == gym_id).all()
        # check if the customers variable empty
        if not customers:
            raise HTTPException(status_code=404, detail=f"Gym with id {gym_id} has no customers")

        return customers
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Server error occurred during search")