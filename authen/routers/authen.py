from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth_credential.models.auth_credential import AuthCredential
from user.models.user import User
from user_role.models.user_role import UserRole
from configs.authentication import verify_password, create_access_token
from configs.database import get_db


router = APIRouter(tags=["Login"])


@router.post("/login", 
             status_code=status.HTTP_200_OK)
async def login_user(
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
    
    user = db.query(User).filter(User.username == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Credentials!"
        )
    if not verify_password(user_credentials.password, user.auth_credential.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Credentials!"
        )
    
    access_token, expire = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token,
            "token_type": "bearer", 
            "user": user, 
            "expire": expire}
