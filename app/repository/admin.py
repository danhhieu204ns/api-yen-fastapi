from fastapi import status, HTTPException
from .. import models, schemas, utils
from sqlalchemy.orm import Session



def get_all_admin(db: Session, 
                  current_user):
    
    admins = db.query(models.UserInfo).filter(models.UserInfo.role_id == utils.get_role_by_name(db, "admin").id).all()
    
    return admins


def get_admin_by_id(id: int, 
                    db: Session, 
                    current_user):
    
    admin = db.query(models.UserInfo).filter(models.UserInfo.id == id, 
                                         models.UserInfo.role_id == utils.get_role_by_name(db, "admin").id).first()
    
    return admin


# def updateUser(newUser: schemas.UserUpdate, 
#                db: Session, 
#                current_user):

#     user = db.query(models.User).filter(models.User.id == current_user.id).first()
#     for key, value in newUser.dict().items():
#         setattr(user, key, value)
    
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     # user.update(newUser.dict(), synchronize_session=False)
#     # db.commit()
    
#     return user


# def re_pwd(new_pwd: schemas.UserRePwd, 
#            db: Session, 
#            current_user):
    
#     user = db.query(models.User).filter(models.User.id == current_user.id)

#     new_pwd.password = utils.hash(new_pwd.password)

#     user.update(new_pwd.dict(), synchronize_session=False)
#     db.commit()

#     return {"message": "Succes!"}

