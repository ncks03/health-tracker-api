import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from dtos.dtos import CustomerDTO
import entities.entities as entities

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

@router.get("/")
async def read_customers(db = Depends(get_db)):
    data = db.query(entities.Customer).group_by(entities.Customer.id)
    return data.all()

@router.get("/{customer_id}")
async def read_customer_by_id(customer_id, db = Depends(get_db)):
    statement = (
        select(entities.Customer)
        .where(entities.Customer.id==customer_id)
    )
    data = db.execute(statement)
    return data.all()

@router.post("/create_customer")
async def create_user(customer: CustomerDTO, db = Depends(get_db)):
    customer = entities.Customer(
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