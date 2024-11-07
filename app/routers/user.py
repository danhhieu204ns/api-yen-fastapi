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


@router.get("/pageable", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.UserPageableResponse)
async def get_user_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(database.get_db)
    ):
     
    return user.get_user_pageable(page, page_size, db)


@router.get("/{id}", 
            status_code=status.HTTP_200_OK,  
            response_model=schemas.UserResponse)
async def get_user_by_id(id: int, 
                        db: Session = Depends(database.get_db)):
    
    return user.get_user_by_id(id, db)


@router.put("/update/{user_id}", 
            status_code=status.HTTP_200_OK,  
            response_model=schemas.UserResponse)
async def update_user(
        user_id: int, 
        newUser: schemas.UserUpdate, 
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):

    return user.update_user(user_id, newUser, db, current_user)


@router.post("/update_pwd", 
            status_code=status.HTTP_200_OK
            )
async def update_pwd(
        new_pwd: schemas.UserUpdatePwd, 
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):

    return user.update_pwd(new_pwd, db, current_user)


@router.post("/re_pwd", 
            status_code=status.HTTP_200_OK
            )
async def re_pwd(
        new_pwd: schemas.UserRePwd, 
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):

    return user.re_pwd(new_pwd, db, current_user)


@router.post("/khoa_tai_khoan/{user_id}", 
            status_code=status.HTTP_200_OK
            )
async def deactivate_user(
        user_id: int, 
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):

    return user.deactivate_user(user_id, db, current_user)


@router.post("/kich_hoat_tai_khoan/{user_id}", 
            status_code=status.HTTP_200_OK
            )
async def activate_user(
        user_id: int ,
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):

    return user.activate_user(user_id, db, current_user)


@router.post("/check", 
               status_code=status.HTTP_200_OK, 
               response_model=schemas.UserResponse)
async def check_user(user_img: str = Form(...), 
                    db: Session = Depends(database.get_db), 
                    current_user = Depends(oauth2.get_current_user)):
    
    return user.check_user_img(user_img, db, current_user)


@router.delete("/delete/{user_id}", 
               status_code=status.HTTP_200_OK)
async def delete_user(
        user_id: int, 
        db: Session = Depends(database.get_db), 
        current_user = Depends(oauth2.get_current_user)
    ):
    
    return user.delete_user(user_id, db, current_user)