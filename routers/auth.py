from typing import Annotated
from datetime import timedelta , datetime
from fastapi import APIRouter, Depends, HTTPException , status ,requests ,responses  , Form
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from jose import jwt , JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router=APIRouter(
    prefix='/auth' ,
    tags=['auth']
)

SECRET_KEY='66e56618daa714b36af9ec698c5df6a3df42ff9bac090ab952eb3c94b39d68d3'
ALGORITM='HS256'
bcrypt_context=CryptContext(schemes=['bcrypt'] , deprecated='auto')
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

class Token(BaseModel):
    access_token :str
    token_type:str
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session, Depends(get_db)]            

def authenticate_user(username:str , password:str , db):
    user=db.query(Users).filter(Users.username ==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password , user.hashed_password):
        return False
    return user
 
def created_access_token(username : str , user_id:int ,role : str,  expires_delta : timedelta):
    encode ={'sub' : username , 'id': user_id , 'role':role}
    expires=datetime.utcnow() + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode ,SECRET_KEY , algorithm=ALGORITM)

async def get_current_user(token:Annotated[str , Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token, SECRET_KEY ,algorithms=[ALGORITM])
        username: str=payload.get('sub')
        user_id: int=payload.get('id')
        user_role: str=payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not validation user .')
        return {'username':username , 'id':user_id , 'user_role':user_role}
    except JWTError :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not validation user  .')

    
@router.post("/register" , response_class=HTMLResponse)
async def register_user(request:requests , email :str =Form(...) ,  username :str =Form(...) ,  firstname :str =Form(...) ,  lastname :str =Form(...) , password :str =Form(...) ,  password2 :str =Form(...) , db:Session=Depends(get_db)):
     validation1=db.query(Users)

@router.post("/" , status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
   create_user_model=Users(
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        status=True
   )
   db.add(create_user_model)
   db.commit()

@router.post("/token" , response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm , Depends()], db:db_dependency):
    user=authenticate_user(form_data.username , form_data.password, db)
    if not user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail='Could not validation user  .')

    token=created_access_token(user.username ,user.id ,user.role,timedelta(minutes=20))

    return {'access_token' : token , 'token_type' : 'bearer'}

