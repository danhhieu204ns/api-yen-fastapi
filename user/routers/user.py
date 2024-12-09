from fastapi import status, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from configs.database import get_db
from configs.authentication import get_current_user, hash_password, validate_pwd
from user.models.user import User
from user.schemas.user import UserCreate, UserUpdate, UserResponse, UserPageableResponse
from auth_credential.models.auth_credential import AuthCredential
import math


router = APIRouter(
    prefix= "/user",
    tags=["User"]
)
    

@router.get("/all", 
            response_model=list[UserResponse], 
            status_code=status.HTTP_200_OK)
async def get_all_users(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).all()
        
        return users
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/pageable", 
            response_model=UserPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_user_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(User).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        users = db.query(User).offset(offset).limit(page_size).all()

        user_pageable_res = UserPageableResponse(
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


@router.get("/{user_id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserResponse)
async def get_user_by_id(
        user_id: int, 
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )
        
        return user
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search/by-name/{name}",
            status_code=status.HTTP_200_OK,  
            response_model=list[UserResponse])
async def get_user_by_name(
        name: str, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).filter(User.full_name.ilike(f"%{name}%")).all()

        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Người dùng không tồn tại")
        
        return users
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.post("/register", 
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: UserCreate,
        db: Session = Depends(get_db), 
    ):
    
    try:
        username = db.query(User).filter(User.username == new_user.username).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tên đăng nhập đã tồn tại"
            )
        validate_pwd(new_user.password)

        new_info = User(
            username=new_user.username, 
            full_name=new_user.full_name,
            email=new_user.email,
            phone_number=new_user.phone_number,
            birthdate=new_user.birthdate,
            address=new_user.address
        )
        db.add(new_auth)
        db.flush()

        new_auth = AuthCredential(
            user_id=new_info.id,
            password=hash_password(new_user.password),
        )        
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        return new_info
    
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
    

@router.post("/import",
             status_code=status.HTTP_201_CREATED)
async def import_user(
        new_users: list[UserCreate], 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        for user in new_users:
            new_user = User(
                username=user.username, 
                full_name=user.full_name,
                email=user.email,
                phone_number=user.phone_number,
                birthdate=user.birthdate,
                address=user.address
            )
            db.add(new_user)
            db.flush()

            new_auth = AuthCredential(
                user_id=new_user.id,
                password=hash_password(user.password),
            )
            db.add(new_auth)
        
        db.commit()
        
        return {"message": "Nhập dữ liệu thành công"}
    
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

    
@router.post("/active/{user_id}",
             status_code=status.HTTP_200_OK)
async def active_user(
        user_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Tài khoản không tồn tại"
            )

        user.update(
            {"active_user": True}, 
            synchronize_session=False
        )
        db.commit()

        return {"message": "Kích hoạt tài khoản thành công"}
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/deactive/{user_id}",
             status_code=status.HTTP_200_OK)
async def deactive_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tài khoản không tồn tại"
            )
        
        user.update(
            {"active_user": False}, 
            synchronize_session=False
        )
        db.commit()

        return {"message": "Vô hiệu hóa tài khoản thành công"}
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Dữ liệu không hợp lệ hoặc vi phạm ràng buộc cơ sở dữ liệu"
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{user_id}", 
            status_code=status.HTTP_200_OK,  
            response_model=UserResponse)
async def update_user(
        user_id: int, 
        newUser: UserUpdate, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
 
    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

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


@router.delete("/delete/{user_id}",
                status_code=status.HTTP_200_OK)
async def delete_user(
        user_id: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        user = db.query(User).filter(User.id == user_id)
        if not user.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng có không tồn tại"
            )

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


@router.delete("/delete_many",
                status_code=status.HTTP_200_OK)
async def delete_many_user(
        user_ids: list[int], 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).filter(User.id.in_(user_ids))
        if not users.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )

        users.delete(synchronize_session=False)
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
    

@router.delete("/delete-all",
                status_code=status.HTTP_200_OK)
async def delete_all_user(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        db.query(User).delete()
        db.commit()

        return {"message": "Xóa tất cả người dùng thành công"}
    
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
    