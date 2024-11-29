from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from user_account.models.user_account import UserAccount
from user_account.schemas.user_account import UserAccountResponseWithRole, UserAccountResponse, UserAccountPageableResponse
from configs.conf import settings
from configs.authentication import hash_password
import math

RESET_PASSWORD = settings.reset_password

router = APIRouter(
    prefix="/user_account",
    tags=["User_Account"],
)

@router.get("/all", 
            response_model=list[UserAccountResponse], 
            status_code=status.HTTP_200_OK)
async def get_user_account(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_accounts = db.query(UserAccount).all()

        return user_accounts
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.get("/pageable", 
            response_model=UserAccountPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_account_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)  
    ):
     
    try:
        total_count = db.query(UserAccount).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        user_accounts = db.query(UserAccount).offset(offset).limit(page_size).all()

        user_accounts_pageable_res = UserAccountPageableResponse(
            user_accounts=user_accounts,
            total_pages=total_pages,
            total_data=total_count
        )

        return user_accounts_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.get("/{id}",
            response_model=UserAccountResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_account_by_id(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id).first()

        if not user_account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Tài khoản không tồn tại")

        return user_account
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
                                

@router.post("/active/{id}",
             status_code=status.HTTP_200_OK)
async def active_user_account(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id)
        if not user_account.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Tài khoản không tồn tại")

        user_account.update({"active_user": True}, 
                            synchronize_session=False)
        db.commit()

        return {"message": "Kích hoạt tài khoản thành công"}
    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.post("/deactive/{id}",
             status_code=status.HTTP_200_OK)
async def deactive_user_account(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id)
        if not user_account.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tài khoản không tồn tại")
        
        user_account.update({"active_user": False}, 
                            synchronize_session=False)
        db.commit()

        return {"message": "Vô hiệu hóa tài khoản thành công"}
    
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.put("/{id}/reset-password",
            status_code=status.HTTP_200_OK)
async def update_user_account(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id)
        if not user_account.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Tài khoản không tồn tại")

        user_account.update({"password": hash_password(RESET_PASSWORD)}, 
                            synchronize_session=False)

        db.commit()    

        return {"message": "Reset mật khẩu thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.put("/{id}/update-password",
            status_code=status.HTTP_200_OK)
async def update_user_account_password(
        id: int,
        password: str,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id)
        if not user_account.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Tài khoản không tồn tại")

        user_account.update({"password": hash_password(RESET_PASSWORD)}, 
                            synchronize_session=False)
        db.commit()

        return {"message": "Cập nhật mật khẩu thành công"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.delete("/{id}/delete",
                status_code=status.HTTP_200_OK)
async def delete_user_account(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_account = db.query(UserAccount).filter(UserAccount.id == id)
        if not user_account.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Tài khoản không tồn tại")

        user_account.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tài khoản thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")


@router.delete("/delete-many",
                status_code=status.HTTP_200_OK)
async def delete_user_accounts(
        ids: list[int],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user_accounts = db.query(UserAccount).filter(UserAccount.id.in_(ids)).all()
        if not user_accounts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Tài khoản không tồn tại")

        db.query(UserAccount).filter(UserAccount.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tài khoản thành công"}
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu")
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
