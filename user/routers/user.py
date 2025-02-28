from io import BytesIO
from fastapi import File, UploadFile, status, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from configs.database import get_db
from configs.authentication import get_current_user, hash_password, validate_pwd
from role.models.role import Role
from user.models.user import User
from user.schemas.user import *
from auth_credential.models.auth_credential import AuthCredential
from user_role.models.user_role import UserRole
from os import getenv
import math
import pandas as pd


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
                username=user[0].username,
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

        return ListUserResponse(
            users=users, 
            tolal_data=len(users)
        )
    
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
                username=user[0].username,
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
    

@router.get("/full-name")
async def get_user_full_name(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).all()
        user_full_names = [UserFullNameResponse(id=u.id, full_name=u.full_name) for u in users]

        return ListUserFullNameResponse(
            users=user_full_names
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.get("/admin-name")
async def get_user_admin_name(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        users = db.query(User)\
            .join(UserRole)\
            .join(Role)\
            .filter(Role.name == "admin")\
            .all()
            
        user_admin_names = [UserFullNameResponse(id=u.id, full_name=u.full_name) for u in users]

        return ListUserFullNameResponse(
            users=user_admin_names
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.get("/export",
            status_code=status.HTTP_200_OK)
async def export_user(
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

        df = pd.DataFrame([{
            "Số thứ tự": index + 1,
            "Họ và Tên": user[0].full_name,
            "Tên người dùng": user[0].username,
            "Email": user[0].email,
            "Số điện thoại": user[0].phone_number,
            "Ngày sinh": user[0].birthdate,
            "Địa chỉ": user[0].address,
            "Đang hoạt động": user[0].is_active,
            "Vai trò": ', '.join(user[1])
        } for index, user in enumerate(users)])
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Users', index=False)
        writer.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="users.xlsx"'
        }
        
        return StreamingResponse(
            output,
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
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
            username=user[0].username,
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
            response_model=UserPageableResponse)
async def search_user(
        search: UserSearch, 
        page: int,
        page_size: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = (
            db.query(
                User,
                func.coalesce(func.array_agg(Role.name).filter(Role.name != None), '{}').label("roles")
            )
            .outerjoin(UserRole, User.id == UserRole.user_id)
            .outerjoin(Role, UserRole.role_id == Role.id)
            .group_by(User.id)
        )

        if search.username:
            users = users.filter(User.username.ilike(f"%{search.username}%"))
        if search.full_name:
            users = users.filter(User.full_name.ilike(f"%{search.full_name}%"))
        if search.phone_number:
            users = users.filter(User.phone_number.ilike(f"%{search.phone_number}%"))
        if search.address:
            users = users.filter(User.address.ilike(f"%{search.address}%"))
        if search.role:
            users = users.join(UserRole).join(Role).filter(Role.name == search.role)

        total_count = users.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        users = users.offset(offset).limit(page_size).all()
        users = [
            UserResponse(
                id=user[0].id,
                full_name=user[0].full_name,
                username=user[0].username,
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

        return UserPageableResponse(
            users=users,
            total_pages=total_pages,
            total_data=total_count
        )
    
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

        # Create all objects first without committing
        new_info = User(
            username=new_user.username, 
            full_name=new_user.full_name,
            email=new_user.email,
            phone_number=new_user.phone_number,
            birthdate=new_user.birthdate,
            address=new_user.address
        )
        db.add(new_info)
        
        # Flush to get the user ID but don't commit yet
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

        # Commit everything at once
        db.commit()

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
    

@router.post("/create-account")
async def create_account(
        account: UserCreateAccount,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    
    try:
        # Check existing username
        username = db.query(User).filter(User.username == account.username).first()
        if username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tên đăng nhập đã tồn tại"
            )
        
        # Check existing email - only if email is provided and not empty
        if account.email and account.email.strip() != '':
            email = db.query(User).filter(User.email == account.email).first()
            if email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email đã tồn tại"
                )

        # Get default password from .env
        default_password = getenv("DEFAULT_PASSWORD")
        if not default_password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Chưa cấu hình mật khẩu mặc định"
            )

        # Create and commit user first
        new_info = User(
            username=account.username,
            full_name=account.full_name,
            email=account.email if account.email and account.email.strip() != '' else None,
            phone_number=account.phone_number if account.phone_number and account.phone_number.strip() != '' else None,
            birthdate=account.birthdate if account.birthdate else None, 
            address=account.address if account.address and account.address.strip() != '' else None
        )
        db.add(new_info)
        db.flush()

        # Create auth credential with default password
        new_auth = AuthCredential(
            user_id=new_info.id,
            hashed_password=hash_password(default_password)
        )
        db.add(new_auth)

        # Assign default user role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không tìm thấy role mặc định"
            )

        new_user_role = UserRole(
            user_id=new_info.id,
            role_id=default_role.id
        )
        db.add(new_user_role)

        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Tạo tài khoản thành công"
            }
        )

    except IntegrityError as e:
        db.rollback()
        print(e)
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


@router.post("/import",
             status_code=status.HTTP_201_CREATED)
async def import_user(
        file: UploadFile = File(...), 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    COLUMN_MAPPING = {
        "Tên người dùng": "username",
        "Họ và Tên": "full_name",
        "Email": "email",
        "Số điện thoại": "phone_number",
        "Ngày sinh": "birthdate",
        "Địa chỉ": "address"
    }

    if file.content_type not in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        raise HTTPException(
            status_code=400, 
            detail="File không hợp lệ. Vui lòng upload file Excel."
        )
    
    content = await file.read()
    
    try:
        df = pd.read_excel(BytesIO(content))

    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Lỗi đọc file: {str(e)}"
        )
    
    try:
        df.rename(columns=COLUMN_MAPPING, inplace=True)

    except KeyError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Tiêu đề cột không hợp lệ: {str(e)}"
        )
    
    existing_usernames = db.query(User.username).all()
    existing_usernames = [username[0] for username in existing_usernames]
    default_role = db.query(Role).filter(Role.name == "user").first()
    
    errors = []
    users_to_create = []
    default_password = getenv("DEFAULT_PASSWORD")

    for index, row in df.iterrows():
        username = row.get("username")

        if not username or username == "":
            errors.append({"row": index + 2, "message": "Tên đăng nhập không được để trống."})
            continue
        if username in existing_usernames:
            errors.append({"row": index + 2, "message": f"Tài khoản '{username}' đã tồn tại."})
            continue

        full_name = row.get("full_name")
        if not full_name:
            errors.append({"row": index + 2, "message": "Họ và tên không được để trống."})

        phone_number = row.get("phone_number")
        if not phone_number or not str(phone_number).isdigit():
            errors.append({"row": index + 2, "message": f"Số điện thoại '{phone_number}' không hợp lệ."})

        # Create new user
        new_user = User(
            username=username,
            full_name=full_name,
            email=None if pd.isna(row.get("email")) else row.get("email"),
            phone_number=phone_number, 
            birthdate=None if pd.isna(row.get("birthdate")) else row.get("birthdate"),
            address=None if pd.isna(row.get("address")) else row.get("address")
        )
        users_to_create.append(new_user)
        
    if errors:
        return JSONResponse(
            status_code=409,
            content={"errors": errors}
        )

    try:
        # Save users first
        db.add_all(users_to_create)
        # Flush to get IDs but don't commit yet
        db.flush()

        # Create auth credentials and role assignments
        auth_credentials = [
            AuthCredential(
                user_id=user.id,
                hashed_password=hash_password(default_password)
            )
            for user in users_to_create
        ]
        
        user_roles = [
            UserRole(
                user_id=user.id,
                role_id=default_role.id
            )
            for user in users_to_create
        ]

        # Save all related objects
        db.bulk_save_objects(auth_credentials)
        db.bulk_save_objects(user_roles)
        
        # Commit everything at once
        db.commit()

        return JSONResponse(
            status_code=201,
            content={"message": "Import người dùng thành công"}
        )

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/activate/{user_id}")
async def activate_user(
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
            {"is_active": True}, 
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
        print(e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/deactivate/{user_id}")
async def deactivate_user(
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
            {"is_active": False}, 
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
        ids: UserDelete, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        users = db.query(User).filter(User.id.in_(ids.list_id))
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
