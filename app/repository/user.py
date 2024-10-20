from fastapi import status, HTTPException
from .. import models, schemas, utils
from sqlalchemy.orm import Session
import re



def create_user(user: schemas.UserCreate, 
                db: Session):
    
    username = db.query(models.User).filter(models.User.username == user.username).first()
    if username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Email is already exist.")
    
    if user.password.__len__() < 8:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one uppercase letter.")

    if not re.search(r'[a-z]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one lowercase letter.")
    
    if not re.search(r'[0-9]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one number.")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one special character.")
    
    role = db.query(models.Role).filter(models.Role.name == "user").first()
    user.password = utils.hash(user.password)
    newUser = models.User(**user.dict(), role_id = role.id)
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return newUser


def get_all_user(db: Session):
    
    users = db.query(models.User).filter(models.User.role_id == utils.get_role_by_name(db, "user").id).all()
    
    return users


def get_user_by_id(id: int, 
                   db: Session):
    
    user = db.query(models.User).filter(models.User.id == id, 
                                        models.User.role_id == utils.get_role_by_name(db, "user").id).first()
    
    return user


def updateUser(newUser: schemas.UserUpdate, 
               db: Session, 
               current_user):

    user = db.query(models.User).filter(models.User.id == current_user.id)
    
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