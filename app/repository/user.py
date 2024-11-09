import math
import base64, os
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, utils


def create_user(user: schemas.UserCreate, db: Session):

    username = db.query(models.UserAuth).filter(models.UserAuth.username == user.username).first()
    if username:
        raise HTTPException(status_code=403, detail="Username already exists.")

    utils.validate_user_credentials(username, user.password)
    role = db.query(models.Role).filter(models.Role.name == "user").first()
    
    new_auth = models.UserAuth(
        username=user.username, 
        password=utils.hash(user.password), 
    )
    db.add(new_auth)
    db.commit()
    db.refresh(new_auth)

    new_info = models.UserInfo(
        name=user.name, 
        birthdate=user.birthdate, 
        address=user.address, 
        phone_number=user.phone_number, 
        role_id=role.id,
        user_auth_id=new_auth.id,
    )
    db.add(new_info)
    db.commit()
    db.refresh(new_info)

    return {"user": new_info}


def get_all_user(db: Session):
    
    users = db.query(models.UserInfo).filter(models.UserInfo.role_id == utils.get_role_by_name(db, "user").id).all()
    
    return users


def get_user_pageable(
        page: int, 
        page_size: int, 
        db: Session
    ):
     
    total_count = db.query(models.UserInfo).count()
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    users = db.query(models.UserInfo).offset(offset).limit(page_size).all()

    user_pageable_res = schemas.UserPageableResponse(
        users=users,
        total_pages=total_pages,
        total_data=total_count
    )

    return user_pageable_res


def get_user_by_id(id: int, 
                   db: Session):
    
    user = db.query(models.UserInfo).filter(models.UserInfo.id == id, 
                                        models.UserInfo.role_id == utils.get_role_by_name(db, "user").id).first()
    
    return user


def update_user(
        user_id: int, 
        newUser: schemas.UserUpdate, 
        db: Session, 
        current_user
    ):

    user = db.query(models.UserInfo).filter(models.UserInfo.id == user_id)
    role = db.query(models.Role).filter(models.Role.name == newUser.role).first()

    user.update(
        {
            "name": str(newUser.name),
            "birthdate": newUser.birthdate,  # Assuming date is already in correct format
            "address": str(newUser.address),
            "phone_number": str(newUser.phone_number),
            "role_id": int(role.id)
        }, 
        synchronize_session=False
    )
    db.commit()

    return user.first()


def update_pwd(new_pwd: schemas.UserUpdatePwd, 
           db: Session, 
           current_user):
    
    user = db.query(models.UserInfo).filter(models.UserInfo.id == current_user.id).first()
    user_auth = db.query(models.UserAuth).filter(models.UserAuth.id == user.user_auth_id)

    new_pwd.password = utils.hash(new_pwd.password)

    user_auth.update(new_pwd.dict(), synchronize_session=False)
    db.commit()

    return {"message": "Succes!"}


def re_pwd(new_pwd: schemas.UserRePwd, 
           db: Session, 
           current_user):
    
    user_auth = db.query(models.UserAuth).filter(models.UserAuth.username == new_pwd.username)

    password = utils.hash("Kgdy@123")

    user_auth.update(
        {
            "password": password,
        }, 
        synchronize_session=False
    )
    db.commit()

    return {"message": "Succes!"}


def deactivate_user(
        user_id: int, 
        db: Session, 
        current_user
    ):
    
    user_info = db.query(models.UserInfo).filter(models.UserInfo.id == user_id)

    user_info.update(
        {
            "status": False,
        }, 
        synchronize_session=False
    )
    db.commit()

    return {"message": "Succes!"}


def activate_user(
        user_id: int, 
        db: Session, 
        current_user
    ):
    
    user_info = db.query(models.UserInfo).filter(models.UserInfo.id == user_id)

    user_info.update(
        {
            "status": True,
        }, 
        synchronize_session=False
    )
    db.commit()

    return {"message": "Succes!"}


def delete_user(
        user_id: int, 
        db: Session, 
        current_user
    ):
    
    user_info = db.query(models.UserInfo).filter(models.UserInfo.id == user_id)

    user_info.delete( 
        synchronize_session=False
    )
    db.commit()

    return {"message": "Succes!"}
