import math
import base64, os
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import models, schemas, utils
from ..face_recognition import add_new_user, check_user


UPLOAD_FOLDER = "app/face_recognition/image"

def create_user(user: schemas.UserCreate, db: Session):

    username = db.query(models.UserAuth).filter(models.UserAuth.username == user.username).first()
    if username:
        raise HTTPException(status_code=400, detail="Username already exists.")

    try:
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


        header, encoded = user.image.split(",", 1)
        image_data = base64.b64decode(encoded)
        filename = f"{new_info.id}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)

        add_new_user.add_new_user(file_path, new_info.id)

        return {"user": new_info}

    except (HTTPException, SQLAlchemyError) as e:
        db.rollback()
        if 'new_info' in locals():
            db.delete(new_info)
            db.commit()
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail="User creation failed. Please try again.")

    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail="Unexpected error occurred. Please try again.")


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


def update_user(newUser: schemas.UserUpdate, 
                db: Session, 
                current_user):

    user = db.query(models.UserInfo).filter(models.UserInfo.id == current_user.id)
    
    user.update(newUser.dict(), synchronize_session=False)
    db.commit()
    db.refresh(user)

    return user


# def re_pwd(new_pwd: schemas.UserRePwd, 
#            db: Session, 
#            current_user):
    
#     user = db.query(models.User).filter(models.User.id == current_user.id)

#     new_pwd.password = utils.hash(new_pwd.password)

#     user.update(new_pwd.dict(), synchronize_session=False)
#     db.commit()

#     return {"message": "Succes!"}


CHECK_FOLDER = "app/repository"

def check_user_img(
    user_img: str, 
    db: Session, 
    current_user
):
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")
    
    header, encoded = user_img.split(",", 1)
    image_data = base64.b64decode(encoded)
    filename = "tmp.jpg"
    file_path = os.path.join(CHECK_FOLDER, filename)
    
    with open(file_path, "wb") as image_file:
        image_file.write(image_data)
    
    try:
        user_info_id = check_user.check_user(file_path)
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == user_info_id).first()

        return user_info

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
