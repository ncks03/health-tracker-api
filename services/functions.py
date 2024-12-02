import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url = os.getenv("DB_URL")
engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Functions
def calculate_age(born):
    today = date.today()
    print(today)
    birth_date = date(year=int(born[0:4]), month=int(born[5:7]), day=int(born[8:10]))
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_daily_calorie_intake():
    pass