from fastapi import status, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from user_info.models.user_info import UserInfo
from user_info.schemas.user_info import UserCreate, UserInfoResponse, UserInfoUpdate, UserInfoPageableResponse
from user_account.models.user_account import UserAccount
from configs.database import get_db
from configs.authentication import get_current_user, hash_password, validate_pwd
import math


router = APIRouter(
    prefix= "/user_info",
    tags=["User_Info"]
)


@router.post("/register", 
             status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: UserCreate,
        db: Session = Depends(get_db), 
    ):
    
    try:
        username = db.query(UserAccount).filter(UserAccount.username == new_user.username).first()
        if username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Tên đăng nhập đã tồn tại")
        validate_pwd(new_user.password)

        new_auth = UserAccount(
            username=new_user.username,
            password=hash_password(new_user.password),
        )
        db.add(new_auth)
        db.flush()

        new_info = UserInfo(
            name=new_user.name,
            birthdate=new_user.birthdate,
            address=new_user.address,
            phone_number=new_user.phone_number,
            user_account_id=new_auth.id,
        )
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        return {"user": new_info}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
    

@router.get("/all", 
            response_model=list[UserInfoResponse], 
            status_code=status.HTTP_200_OK)
async def get_all_user(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(UserInfo).all()
        
        return users
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/pageable", 
            response_model=UserInfoPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(UserInfo).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        users = db.query(UserInfo).offset(offset).limit(page_size).all()

        user_pageable_res = UserInfoPageableResponse(
            users=users,
            total_pages=total_pages,
            total_data=total_count
        )

        return user_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search/by-id/{id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserInfoResponse)
async def get_user_by_id(
        id: int, 
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(UserInfo).filter(UserInfo.id == id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Người dùng có id {id} không tồn tại")
        
        return user
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search/by-name/{name}",
            status_code=status.HTTP_200_OK,  
            response_model=list[UserInfoResponse])
async def get_user_by_name(
        name: str, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(UserInfo).filter(UserInfo.name.ilike(f"%{name}%")).all()

        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Người dùng có tên {name} không tồn tại")
        
        return users
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/update/{id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserInfoResponse)
async def update_user(
        id: int, 
        newUser: UserInfoUpdate, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
 
    try:
        user = db.query(UserInfo).filter(UserInfo.id == id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Người dùng có id {id} không tồn tại")

        user.update(newUser.dict(), synchronize_session=False)
        db.commit()

        return user.first()
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/delete/{id}",
                status_code=status.HTTP_200_OK)
async def delete_user(
        id: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(UserInfo).filter(UserInfo.id == id)
        if not user.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Người dùng có id {id} không tồn tại")

        user.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa người dùng thành công"}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
