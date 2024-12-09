from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.conf import settings
from configs.database import get_db
from configs.authentication import get_current_user, hash_password
from auth_credential.models.auth_credential import AuthCredential
from auth_credential.schemas.auth_credential import AuthCredentialResponse, AuthCredentialPageableResponse
import math


RESET_PASSWORD = settings.reset_password


router = APIRouter(
    prefix="/auth-credential",
    tags=["Auth_Credentials"]
)


@router.get("/all", 
            response_model=list[AuthCredentialResponse], 
            status_code=status.HTTP_200_OK)
async def get_auth_credentials(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credentials = db.query(AuthCredential).all()

        return auth_credentials
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable", 
            response_model=AuthCredentialPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_auth_credentials_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)  
    ):
     
    try:
        total_count = db.query(AuthCredential).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        auth_credentials = db.query(AuthCredential).offset(offset).limit(page_size).all()

        auth_credentials_pageable_res = AuthCredentialPageableResponse(
            auth_credentials=auth_credentials,
            total_pages=total_pages,
            total_data=total_count
        )

        return auth_credentials_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{auth_credential_id}",
            response_model=AuthCredentialResponse, 
            status_code=status.HTTP_200_OK)
async def get_auth_credential_by_id(
        auth_credential_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credential = db.query(AuthCredential).filter(AuthCredential.id == auth_credential_id).first()

        if not auth_credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        return auth_credential
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/reset-password/{auth_credential_id}",
            status_code=status.HTTP_200_OK)
async def reset_user_password(
        auth_credential_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credential = db.query(AuthCredential).filter(AuthCredential.id == auth_credential_id)
        if not auth_credential.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        auth_credential.update(
            {"password": hash_password(RESET_PASSWORD)}, 
            synchronize_session=False
        )
        db.commit()    

        return {"message": "Reset mật khẩu thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update-password/{auth_credential_id}",
            status_code=status.HTTP_200_OK)
async def update_user_password(
        auth_credential_id: int,
        password: str,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credential = db.query(AuthCredential).filter(AuthCredential.id == auth_credential_id)
        if not auth_credential.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        auth_credential.update(
            {"password": hash_password(password)}, 
            synchronize_session=False
        )
        db.commit()

        return {"message": "Cập nhật mật khẩu thành công"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete/{auth_credential_id}",
                status_code=status.HTTP_200_OK)
async def delete_auth_credential(
        auth_credential_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credential = db.query(AuthCredential).filter(AuthCredential.id == auth_credential_id)
        if not auth_credential.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        auth_credential.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tài khoản thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many",
                status_code=status.HTTP_200_OK)
async def delete_user_accounts(
        auth_credential_ids: list[int],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        auth_credentials = db.query(AuthCredential).filter(AuthCredential.id.in_(auth_credential_ids))
        if not auth_credentials.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tài khoản không tồn tại")

        auth_credentials.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tài khoản thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
