#pydantic base models 
from pydantic import BaseModel, EmailStr,Field
from .enums import Gender
from typing import Optional
from datetime import datetime,date

class UserBase(BaseModel):
  email: EmailStr
  username:str
  name:str
  password:str
  created_date:datetime 
  dob:date
  gender:Optional[Gender] = None 
  bio:Optional[str] = None 
  location:Optional[str] = None 
  profile_pic : Optional[str] = None 

class UserCreate(UserBase):
  password:str

class UserUpdate(BaseModel):
  username:Optional[str] = None 
  name:Optional[str]  = None
  # dob:Optional[date]  = None
  gender:Optional[Gender]  = None
  bio:Optional[str]  = None
  profile_pic : Optional[str]  = None
  location:Optional[str]  = None

class User(UserBase):
  id:int
  created_date:datetime

  class Config:
    from_attributes = True 

class Token(BaseModel):
  access_token: str
  token_type: str

class UserResults(BaseModel):
  email: EmailStr
  username:str
  name:str
  dob:date
  gender:Optional[Gender] = None 
  bio:Optional[str] = None 
  location:Optional[str] = None 
  profile_pic : Optional[str] = None

class TokenData(BaseModel):
  username: str | None = None 