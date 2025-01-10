### Dependencies ###
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select

### Imports ###
from routers import customers, gyms, goals, progress
from models.entities import Customer as CustomerTable
from services.functions import get_db, calculate_daily_calories_all_customers

# API Initialisation
app = FastAPI()

@app.get("/")
def read_root():
    text = "the server is up and running"
    version = "V1.3.4"
    return text + " " + version

@app.get("/daily_intake_all")
async def get_daily_intake_all(from_start_date: Optional[bool] = False,
                                        db = Depends(get_db)):
    try:
        statement = select(CustomerTable.id).order_by(CustomerTable.id.asc())

        customer_ids = db.execute(statement).scalars().all()

        if not customer_ids:
            raise HTTPException(
                status_code=404,
                detail=f"No customers found"
            )

        detailed_daily_cal_intake = calculate_daily_calories_all_customers(customer_ids, from_start_date, db)

        response_data = {"data": detailed_daily_cal_intake}

        return response_data

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

app.include_router(customers.router)
app.include_router(gyms.router)
app.include_router(goals.router)
app.include_router(progress.router)
