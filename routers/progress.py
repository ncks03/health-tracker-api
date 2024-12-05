import os

from dns.rdtypes.ANY.RRSIG import posixtime_to_sigtime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, APIRouter, HTTPException
from schemas.dtos import ProgressDTO
from models.entities import Gym, Progress, Customer

# Load environment variables
### DO NOT PUSH .ENV TO GIT ###
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME") #Insert username variable name here
DB_PASSWORD = os.getenv("DB_PASSWORD") #Insert password variable name here
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
    prefix="/progress",
    tags=["progress"]
)

@router.get("/")
async def read_progress(db = Depends(get_db)):
    try:
        progresses = db.query(Progress).all()
        if progresses:
            return progresses
        else:
            raise HTTPException(status_code=404, detail="No progresses found")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="internal server error")

@router.get("/{progress_id}")
async def get_progress_by_id(progress_id: int, db = Depends(get_db)):
    try:
        progress = db.query(Progress).filter(Progress.id == progress_id).first()
        customer = db.query(Customer).filter(Customer.id == progress.customer_id).first()
        if progress:
            progress.customer = f"{customer.first_name} {customer.last_name}"
            return progress
        else:
            raise HTTPException(status_code=404, detail=f"No progress found with id {progress_id}")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="internal server error")