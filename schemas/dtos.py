from pydantic import BaseModel, PositiveInt, PastDate, AwareDatetime, FutureDate
from datetime import date

from pydantic.v1 import PositiveFloat


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

class GymDTO(BaseModel):
    name: str
    address_place: str

class ProgressDTO(BaseModel):
    weight: PositiveInt

class GoalDTO(BaseModel):
    weight_goal: PositiveInt
    start_date: date
    end_date: FutureDate

