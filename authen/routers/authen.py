from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from user_account.models.user_account import UserAccount
from user_info.models.user_info import UserInfo
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
    
    user_account = db.query(UserAccount).filter(UserAccount.username == user_credentials.username).first()

    if not user_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    if not verify_password(user_credentials.password, user_account.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    
    access_token = create_access_token(data={"user_id": user_account.id})
    user_info = db.query(UserInfo).filter(UserInfo.user_account_id == user_account.id).first()
    roles = db.query(UserRole).filter(UserRole.user_account_id == user_account.id).first()

    return {"access_token": access_token,
            "token_type": "bearer", 
            "user": user_info, 
            "role": roles}
