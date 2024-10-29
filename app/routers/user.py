import base64
from datetime import date
from typing import Optional
from fastapi import File, Form, UploadFile, status, APIRouter, Depends
from .. import schemas, database, oauth2
from ..repository import user
from sqlalchemy.orm import Session


router = APIRouter(
    prefix= "/user",
    tags=["Users"]
)


@router.post("/register", 
             status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Session = Depends(database.get_db), 
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    birthdate: date = Form(...),
    address: str = Form(...),
    phone_number: str = Form(...),
    image: str = Form(...)
):
    user_data = schemas.UserCreate(
        username=username,
        password=password,
        name=name,
        birthdate=birthdate,
        address=address,
        phone_number=phone_number,
        image=image
    )

    return user.create_user(user_data, db)


@router.get("/all", 
            status_code=status.HTTP_200_OK,  
            response_model=list[schemas.UserResponse])
async def get_all_user(db: Session = Depends(database.get_db)):
    
    return user.get_all_user(db)


@router.get("/{id}", 
            status_code=status.HTTP_200_OK,  
            response_model=schemas.UserResponse)
async def get_user_by_id(id: int, 
                        db: Session = Depends(database.get_db)):
    
    return user.get_user_by_id(id, db)


@router.put("/update", 
            status_code=status.HTTP_202_ACCEPTED,  
            response_model=schemas.UserResponse)
async def update_user(newUser: schemas.UserUpdate, 
                      db: Session = Depends(database.get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return user.update_user(newUser, db, current_user)


# @router.put("/update_pwd")
# async def updateUser(new_pwd: schemas.UserRePwd, 
#                      db: Session = Depends(database.get_db), 
#                      current_user = Depends(oauth2.get_current_user)):

#     return user.re_pwd(new_pwd, db, current_user)