from fastapi import Depends, APIRouter
from dtos.dtos import CustomerDTO
from entities.entities import Customer as CustomerEntity
from main import get_db

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.get("/")
def read_customers():
    pass

@router.post("/create_customer")
def create_user(customer: CustomerDTO, db = Depends(get_db)):
    customer= CustomerEntity(
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