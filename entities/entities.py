from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

### Database objects ###
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gym_id = Column(Integer, ForeignKey("gyms.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    length = Column(Integer, nullable=False)
    activity_level = Column(Integer, nullable=False)
    goals = relationship("Goal", back_populates="customers")

class Gym(Base):
    __tablename__ = "gyms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    customers = relationship("Gym", back_populates="customers")
    address_place = Column(String, nullable=False)

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    date = Column(Date, nullable=False)
    weight = Column(Integer, nullable=False)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    weight_goal = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
