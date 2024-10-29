import base64, os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..face_recognition import add_new_user


UPLOAD_FOLDER = "app/face_recognition/image"

def create_user(user: schemas.UserCreate, 
                db: Session):
    
    username = db.query(models.UserAuth).filter(models.UserAuth.username == user.username).first()
    try:
        utils.validate_user_credentials(username, user.password)
        role = db.query(models.Role).filter(models.Role.name == "user").first()
        new_info = models.UserInfo(
            name=user.name, 
            birthdate=user.birthdate, 
            address=user.address, 
            phone_number=user.phone_number, 
            role_id=role.id
        )
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        new_auth = models.UserAuth(
            username=user.username, 
            password=utils.hash(user.password), 
            user_id=new_info.id)
        db.add(new_auth)
        db.commit()
        
        header, encoded = user.image.split(",", 1)
        image_data = base64.b64decode(encoded)
        filename = f"{new_info.id}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)
        
        add_new_user.add_new_user(file_path, new_info.id)

        return {"user": new_info}
    
    except HTTPException as e:
        print(e.detail)


def get_all_user(db: Session):
    
    users = db.query(models.UserInfo).filter(models.UserInfo.role_id == utils.get_role_by_name(db, "user").id).all()
    
    return users


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