from typing import Annotated
from datetime import timedelta , datetime
from fastapi import APIRouter, Depends, HTTPException ,Path
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt , JWTError
from .auth import get_current_user

router=APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
       db.close()

db_dependency=Annotated[Session, Depends(get_db)]            
user_dependency=Annotated[dict , Depends(get_current_user)]

@router.get("/user" , status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency ,db:db_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Authentication Failed.')
    return db.query(Users.first_name).all

@router.delete("/user/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency  , db :db_dependency , user_id:int = Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Authentication Failed.')
    user_model=db.query(Users).filter(Users.id==user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404 , detail='user not found')
    db.query(Users).filter(Users.id==user_id).delete()
    db.commit()
