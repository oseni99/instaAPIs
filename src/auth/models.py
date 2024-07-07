#db models 
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Enum,DATETIME
from ..database import Base
from .enums import Gender
from datetime import datetime,timezone,date
from sqlalchemy.orm import validates

class User(Base):
  __tablename__ = "users"
  id = Column(Integer,primary_key=True,index=True)
  email = Column(String, unique=True,index=True,nullable=False)
  username = Column(String, unique=True,index=True,nullable=False)
  name = Column(String,nullable=False)
  password = Column(String,nullable=False)
  created_date = Column(DATETIME, default=datetime.now(timezone.utc))

  #profile related 

  dob = Column(Date)
  gender = Column(Enum(Gender))
  profile_pic = Column(String)
  bio = Column(String)
  location = Column(String)

  @validates('dob')
  def validate_dob(self, key, dob):
    if dob >= date.today():
        raise ValueError("Date of birth must be in the past")
    return dob