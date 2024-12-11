import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import date

from models.entities import Customer as CustomerTable
from models.entities import Goal as GoalsTable
from models.entities import Progress as ProgressTable

load_dotenv()

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
    birth_date = born
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def violates_constraint(level):
    if level < 1.2 or level > 1.725:
        return True
    else:
        return False


def calculate_daily_calories(current_weight, weight_goal, deadline_days, height, age, gender, activity_level):
    """
    Parameters:
    - current_weight: Current weight in kg
    - goal_weight: Desired weight in kg
    - deadline_days: Number of days to achieve the goal
    - height: Height in cm
    - age: Age in years
    - gender: 'male' or 'female'
    - activity_level: between 1.2 and 1.725

    Returns:
    - Daily calorie intake (int)
    """
    # BMR calculation
    if gender == 'male':
        bmr = 10 * current_weight + 6.25 * height - 5 * age + 5
    elif gender == 'female':
        bmr = 10 * current_weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'")



    total_energy_exp = bmr * activity_level  # Total Daily Energy Expenditure

    # Caloric deficit calculation
    weight_change = current_weight - weight_goal  # kg
    total_calories_to_lose = weight_change * 7700  # 1kg = 7700 calories
    daily_deficit = total_calories_to_lose / deadline_days

    # Daily calorie intake
    daily_calories = total_energy_exp - daily_deficit

    return round(daily_calories, 2)


def get_data_from_db_to_calculate(customer_id, db):
    result = db.execute(
        select(
            ProgressTable.weight,
            GoalsTable.weight_goal,
            GoalsTable.start_date,
            GoalsTable.end_date,
            CustomerTable.activity_level,
            CustomerTable.length,
            CustomerTable.gender,
            CustomerTable.birth_date
        )
        .join(GoalsTable, GoalsTable.customer_id == ProgressTable.customer_id)
        .join(CustomerTable, CustomerTable.id == ProgressTable.customer_id)
        .where(ProgressTable.customer_id == customer_id)
        .order_by(ProgressTable.date.desc(), GoalsTable.start_date.desc())
        .limit(1)
    ).fetchone()

    # error handling will happen at the endpoint
    if not result:
        return None

    # Convert the result into a dictionary
    result_data = dict(result._mapping)
    return result_data
