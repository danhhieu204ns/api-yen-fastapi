import base64, os
from fastapi import Form, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, utils, oauth2
from ..database import get_db


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
