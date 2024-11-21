from pydantic import BaseModel, PositiveInt, PastDate, AwareDatetime, FutureDate
from datetime import date

# Response models

class UserResponse(BaseModel):
    name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt

class CustomerResponse(BaseModel):
    gym_id: PositiveInt
    first_name: str
    last_name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt
    activity_level: PositiveInt

class GymResponse(BaseModel):
    name: str
    address_place: str

class ProgressResponse(BaseModel):
    customer_id: PositiveInt
    date: PastDate
    weight: PositiveInt

class GoalResponse(BaseModel):
    id: int
    customer_id: PositiveInt
    weight_goal: PositiveInt
    start_date: date
    end_date: FutureDate
