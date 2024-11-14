import psycopg2
from sqlalchemy import Base, Column, String, Integer, ForeignKey, Date

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