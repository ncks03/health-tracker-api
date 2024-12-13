import os
from time import strptime

from fastapi.exceptions import HTTPException

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import date, datetime

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

def calculate_daily_calories_and_macros(current_weight, weight_goal, deadline_days, height, age, gender,
                                        activity_level):
    """
    Enhanced calorie and macro calculation with personalized nutritional breakdown.

    Parameters:
    - current_weight: Current weight in kg
    - weight_goal: Desired weight in kg
    - deadline_days: Number of days to achieve the goal
    - height: Height in cm
    - age: Age in years
    - gender: 'male' or 'female'
    - activity_level: between 1.2 and 1.725

    Returns:
    - Dictionary with detailed nutritional information
    """

    # BMR calculation
    if gender == 'male':
        bmr = 10 * current_weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * current_weight + 6.25 * height - 5 * age - 161

    total_energy_exp = bmr * activity_level  # Total Daily Energy Expenditure

    # Caloric deficit calculation
    weight_change = current_weight - weight_goal  # kg
    total_calories_to_lose = weight_change * 7700  # 1kg = 7700 calories
    daily_deficit = total_calories_to_lose / deadline_days

    # Daily calorie intake
    daily_calories = total_energy_exp - daily_deficit

    # Macro and micronutrient calculation with nested loops
    macro_profiles = {
        'weightloss': {
            'protein_ratio': (0.35, 0.4),  # Higher protein for muscle preservation
            'carb_ratio': (0.3, 0.35),
            'fat_ratio': (0.25, 0.3)
        },
        'maintenance': {
            'protein_ratio': (0.3, 0.35),
            'carb_ratio': (0.4, 0.45),
            'fat_ratio': (0.2, 0.25)
        },
        'musclegain': {
            'protein_ratio': (0.4, 0.45),  # Higher protein for muscle growth
            'carb_ratio': (0.35, 0.4),
            'fat_ratio': (0.2, 0.25)
        }
    }

    goal_type = 'weightloss' if weight_change > 0 else 'musclegain' if weight_change < 0 else 'maintenance'

    # Nested loop to dynamically calculate macro ranges and micronutrient needs
    macro_breakdown = {}
    macronutrient_categories = ['protein', 'carb', 'fat']

    base_value = 0

    for macro in macronutrient_categories:
        min_ratio, max_ratio = macro_profiles[goal_type][f'{macro}_ratio']

        # First nested loop: calculate macro ranges
        for precision in range(10):  # Allow for precision adjustments
            base_value = daily_calories * ((min_ratio + max_ratio) / 2)

        # Calculate final macro values
        macro_breakdown[macro] = {
            'grams': round(base_value / (4 if macro != 'fat' else 9), 2),
            'calories': round(base_value, 2),
            'percentage': round((base_value / daily_calories) * 100, 2)
        }

    return {
        'total_daily_calories': round(daily_calories, 2),
        'macronutrients': macro_breakdown,
        'goal_type': goal_type
    }

def calculate_daily_calories_all_customers(customer_ids, from_start_date, db):
    result = []

    for customer_id in customer_ids:
        data = get_data_from_db_to_calculate(int(customer_id), db)
        if not data:
            raise HTTPException(status_code=404, detail='No data found')

        weight = int(data["weight"])
        weight_goal = data["weight_goal"]
        height = data["length"]
        age = calculate_age(data["birth_date"])
        gender = data["gender"]
        activity_level = data["activity_level"]

        if from_start_date:
            deadline_in_days = (data["end_date"] - data["start_date"]).days
        else:
            deadline_in_days =  (data["end_date"] - date.today()).days

        calculation = calculate_daily_calories_and_macros(weight, weight_goal, deadline_in_days, height, age, gender, activity_level)

        result.append(calculation)

    return result
