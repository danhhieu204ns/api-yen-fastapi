import base64, os
from fastapi import Form, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, utils, oauth2
from ..database import get_db
from ..face_recognition.check_user import check_user


router = APIRouter(tags=["Login"])

@router.post("/login", 
             status_code=status.HTTP_200_OK)
async def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(),
                     db: Session = Depends(get_db)):
    
    user_auth = db.query(models.UserAuth).filter(models.UserAuth.username == user_credentials.username).first()

    if not user_auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    if not utils.verify(user_credentials.password, user_auth.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    
    access_token, expire = oauth2.create_access_token(data={"user_id": user_auth.id})
    role = db.query(models.Role).filter(models.Role.id == user_auth.user_info.role_id).first()

    return {"access_token": access_token,
            "token_type": "bearer", 
            "user": user_auth.user_info, 
            "role": role.name, 
            "expire": expire}


UPLOAD_FOLDER = "app/routers"

@router.post("/login_face", 
             status_code=status.HTTP_200_OK)
async def login_user(image: str = Form(...), db: Session = Depends(get_db)):
    header, encoded = image.split(",", 1)
    image_data = base64.b64decode(encoded)
    filename = "tmp.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, "wb") as image_file:
        image_file.write(image_data)
    
    try:
        user_info_id = check_user(file_path)
        user_info = db.query(models.UserInfo).filter(models.UserInfo.id == user_info_id).first()
        
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials!")
        
        access_token, expire = oauth2.create_access_token(data={"user_id": user_info.id})
        role = db.query(models.Role).filter(models.Role.id == user_info.role_id).first()

        return {"access_token": access_token,
                "token_type": "bearer", 
                "user": user_info, 
                "role": role.name, 
                "expire": expire}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)