
from fastapi import FastAPI,Depends,HTTPException,Path
from sqlalchemy.orm import Session
from typing import Annotated
import models
from pydantic import BaseModel , Field
from database import engine , SessionLocal
from models import Users
from starlette import status
from routers import auth , admin


app=FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)

    
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
       db.close()
    
db_dependency = Annotated[Session , Depends(get_db)]      
@app.get('/')
async def read_all(db: db_dependency):
    return db.query(Users).all()  

class Usersequest(BaseModel):  
    username:str =Field(min_length=8 , max_length=20)
    password:str =Field(min_length=8 , max_length=20)
    status:bool  
    


@app.get("/user/{user_id}" , status_code=status.HTTP_200_OK)
async def read_user(db:db_dependency, user_id:int=Path(gt=0)):
    user_model= db.query(Users).filter(Users.id == user_id).first()
    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404 , detail='User not found')


@app.post("/user", status_code=status.HTTP_201_CREATED)
async def creat_user(db:db_dependency ,user_request:Usersequest):
    user_model=Users(**user_request.dict())

    db.add(user_model)
    db.commit()


@app.put("/user/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db:db_dependency , user_request:Usersequest, user_id:int =Path(gt=0)):
    user_model=db.query(Users).filter(Users.id==user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404 , detail='user not found')
    user_model.username=user_request.username
    user_model.password=user_request.password


@app.delete("/user/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
async def  delet_user(db: db_dependency , user_id: int=Path(gh=0)):
    user_model=db.query(Users).filter
    if user_model is None:
        raise HTTPException(status_code=404 , detial='user not foand')
    db.query(Users).filter(Users.id==user_id).delete()
    db.commit()