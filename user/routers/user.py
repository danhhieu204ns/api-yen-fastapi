from fastapi import status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from configs.database import get_db
from configs.authentication import get_current_user, hash_password, validate_pwd
from role.models.role import Role
from user.models.user import User
from user.schemas.user import ListUserResponse, UserCreate, UserSearch, UserUpdate, UserResponse, UserPageableResponse
from auth_credential.models.auth_credential import AuthCredential
import math
from user_role.models.user_role import UserRole


router = APIRouter(
    prefix= "/user",
    tags=["User"]
)
    

@router.get("/all",
            response_model=ListUserResponse,
            status_code=status.HTTP_200_OK)
async def get_all_users(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
        )
        users = query.all()
        
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                email=user[0].email,
                phone_number=user[0].phone_number,
                birthdate=user[0].birthdate,
                address=user[0].address,
                is_active=user[0].is_active,
                created_at=user[0].created_at,
                roles=user[1]
            )
            for user in users
        ]

        return ListUserResponse(users=users)
    
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
        
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
        )
        users = query.all()
        
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                email=user[0].email,
                phone_number=user[0].phone_number,
                birthdate=user[0].birthdate,
                address=user[0].address,
                is_active=user[0].is_active,
                created_at=user[0].created_at,
                roles=user[1]
            )
            for user in users
        ]

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
        query = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
            .filter(User.id == user_id)
        )
        user = query.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Người dùng không tồn tại"
            )
        
        user = UserResponse(
            id=user[0].id,
            full_name=user[0].full_name,
            email=user[0].email,
            phone_number=user[0].phone_number,
            birthdate=user[0].birthdate,
            address=user[0].address,
            is_active=user[0].is_active,
            created_at=user[0].created_at,
            roles=user[1]
        )

        return user
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/search",
            status_code=status.HTTP_200_OK,  
            response_model=list[UserResponse])
async def search_user(
        search: UserSearch, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User)
        if search.full_name:
            users = users.filter(User.full_name.ilike(f"%{search.full_name}%"))
        if search.email:
            users = users.filter(User.email == search.email)
        if search.phone_number:
            users = users.filter(User.phone_number == search.phone_number)
        if search.birthdate:
            users = users.filter(User.birthdate == search.birthdate)
        if search.address:
            users = users.filter(User.address.ilike(f"%{search.address}%"))
        if search.is_active:
            users = users.filter(User.is_active == search.is_active)

        users = users.all()

        return users
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.post("/register", 
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
        db.add(new_info)
        db.flush()

        new_auth = AuthCredential(
            user_id=new_info.id,
            hashed_password=hash_password(new_user.password),
        )        
        db.add(new_auth)

        register_role = db.query(Role).filter(Role.name == "user").first()

        new_user_role = UserRole(
            user_id=new_info.id,
            role_id=register_role.id
        )
        db.add(new_user_role)

        db.commit()
        db.refresh(new_info)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content={
                "message": "Tạo tài khoản thành công"
            }
        )
    
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
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content={
                "message": "Nhập dữ liệu thành công"
            }
        )
    
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

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Kích hoạt tài khoản thành công"
            }
        )
    
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

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Vô hiệu hóa tài khoản thành công"
            }
        )
    
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

        user.update(
            newUser.dict(), 
            synchronize_session=False
        )
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Cập nhật người dùng thành công"
            }
        )
    
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
                detail=f"Người dùng không tồn tại"
            )

        user.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa người dùng thành công"
            }
        )
    
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

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa người dùng thành công"
            }
        )
    
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

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "message": "Xóa tất cả người dùng thành công"
            }
        )
    
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
    