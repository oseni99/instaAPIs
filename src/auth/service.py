from datetime import datetime, timedelta, timezone
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from pydantic import EmailStr
from .models import User
from sqlalchemy import or_
from jwt.exceptions import InvalidTokenError
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from .import schemas 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#check if user already exists 
async def existing_user(db:Session, username:str):
  try:
    db_user = db.query(User).filter((User.username == username)|(User.email == username)).first()
    return db_user
  except Exception as e:
    return f"An error occured at {e}"

#get a user based on the username 

async def get_user(db:Session, username:str):
  user = db.query(User).filter(User.username == username).first()
  return user 

async def create_access_token(username:str,id:int, expires_delta: timedelta | None = None):
    to_encode = {
      "username":username,
      "id":id
      }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_user_id(db:Session,id:int):
  return db.query(User).filter(User.id == id).first()

async def create_user(request:schemas.UserCreate,db:Session):
  new_user = User(
    email = request.email,
    username = request.username,
    name = request.name,
    password = pwd_context.hash(request.password),
    gender = request.gender,
    location = request.location,
    profile_pic = request.profile_pic,
    bio = request.bio,
    dob = request.dob
    )
  db.add(new_user)
  db.commit()
  db.refresh(new_user)
  return new_user

async def authenticate_user(db:Session,username:str,password:str):
  db_user = await existing_user(db,username)
  if not db_user:
    return None 
  elif not pwd_context.verify(password, db_user.password):
    return False 
  return db_user

async def update_user_svc(db:Session,username:str,request:schemas.UserUpdate):
  db_user = db.query(User).filter(User.username == username).first()
  if not db_user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="User not found")
  
  if request.username is not None:
    db_user.username = request.username
  if request.name is not None:
    db_user.name = request.name
  if request.gender is not None:
    db_user.gender = request.gender
  if request.profile_pic is not None:
    db_user.profile_pic = request.profile_pic
  if request.bio is not None:
    db_user.bio = request.bio
  if request.location is not None:
    db_user.location = request.location
    db_user.bio = request.bio
  if request.profile_pic is not None:
    db_user.profile_pic = request.profile_pic
  db.commit()
  db.refresh(db_user)
  return db_user