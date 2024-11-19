from pydantic import BaseModel, PositiveInt, PastDate, AwareDatetime, FutureDate

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
    activity_level: PositiveInt

class GymDTO(BaseModel):
    name: str
    address_place: str

class ProgressDTO(BaseModel):
    customer_id: PositiveInt
    date: AwareDatetime
    weight: PositiveInt

class GoalDTO(BaseModel):
    customer_id: PositiveInt
    weight_goal: PositiveInt
    start_date: FutureDate
    end_date: FutureDate