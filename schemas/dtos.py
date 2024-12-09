from typing import Optional

from pydantic import BaseModel, PositiveInt, PastDate, FutureDate, PositiveFloat
from datetime import date


# DTO (Data Transfer Object)

class UserDTO(BaseModel):
    name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt

class CustomerDTO(BaseModel):
    gym_id: PositiveInt
    first_name: str
    last_name: str
    birth_date: PastDate
    gender: str
    length: PositiveInt
    activity_level: PositiveFloat

class CustomerUpdateDTO(BaseModel):
    gym_id: Optional[PositiveInt] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[PastDate] = None
    gender: Optional[str] = None
    length: Optional[PositiveInt] = None
    activity_level: Optional[PositiveFloat] = None

class GymDTO(BaseModel):
    name: str
    address_place: str

class ProgressDTO(BaseModel):
    weight: PositiveInt

class GoalDTO(BaseModel):
    weight_goal: PositiveInt
    start_date: date
    end_date: FutureDate

