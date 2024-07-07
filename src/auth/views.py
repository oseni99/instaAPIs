#apis are defined APIS only
#signing up 
#get current user 
#update user 
#reset password 

from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .schemas import UserBase,UserCreate,UserUpdate,Token,UserResults
from ..database import get_db
from typing import Annotated
from .import models
from .service import (
  oauth2_scheme,
  existing_user,
  create_access_token,
  get_current_user,
  authenticate_user,
  create_user as create_user_svc,
  update_user_svc
)

router = APIRouter(
  prefix="/auth",
  tags=["auth"]
  )


#signup route
@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def create_user(request:UserCreate,db:Session = Depends(get_db)):
  #check if user already exists 
  db_user = await existing_user(db,request.username)
  if db_user:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Username or Email already in use",
      )
  db_user = await create_user_svc(request,db)
  access_token = await create_access_token(request.username,db_user.id)

  return {
    "access_token": access_token,
    "token_type":"bearer",
    "username":request.username
    }

#login to generate token
@router.post("/login",status_code=status.HTTP_201_CREATED)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(get_db)) ->Token:
  db_user = await authenticate_user(db,form_data.username,form_data.password)
  if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
  access_token = await create_access_token(db_user.username,db_user.id)
  return Token(access_token=access_token,token_type="bearer")

# #get current user 
# async def current_user(token:str,db:Session = Depends(get_db)):
#   return await get_current_user(db,token)


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserResults)
async def get_current_active_user(token:str,db:Session = Depends(get_db)):
  user =  await get_current_user(db,token)
  return user 

#update user 

@router.put("/{username}",status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
  username:str,
  token:str,
  request:UserUpdate,
  db:Session = Depends(get_db)
  ):
  db_user = await get_current_user(db,token)
  if db_user.username != username:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="You are not authorised to update this user"
      )
  updated_user = await update_user_svc(db,username,request)
  return updated_user