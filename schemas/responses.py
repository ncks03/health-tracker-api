from pydantic import BaseModel, PositiveInt, PositiveFloat, PastDate, AwareDatetime, FutureDate
from datetime import date

# Response models

class UserResponse(BaseModel):
    name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt
    gym_id: PositiveInt
    activity_level: PositiveFloat

class SingleCustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt
    weight: int
    gym_id: PositiveInt
    activity_level: PositiveFloat

class GymResponse(BaseModel):
    id: int
    name: str
    address_place: str

class ProgressResponse(BaseModel):
    customer_id: PositiveInt
    date: PastDate
    weight: PositiveInt

class CustomerProgressResponse(BaseModel):
    date: PastDate
    weight: PositiveInt

class CustomerGoalResponse(BaseModel):
    id: int
    weight_goal: PositiveInt
    start_date: date
    end_date: date

class GoalResponse(BaseModel):
    id: int
    customer_id: PositiveInt
    customer_name : str
    weight_goal: PositiveInt
    start_date: date
    end_date: date
