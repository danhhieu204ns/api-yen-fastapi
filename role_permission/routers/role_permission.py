import math
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from permission.models.permission import Permission
from role.models.role import Role
from role_permission.models.role_permission import RolePermission
from role_permission.schemas.role_permission import *


router = APIRouter(
    prefix="/role-permission",
    tags=["Role_Permission"],
)


@router.get("/all", 
            response_model=ListRolePermissionResponse, 
            status_code=status.HTTP_200_OK)
async def get_role_permissions(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = db.query(RolePermission).all()

        return ListRolePermissionResponse(
            role_permissions=role_permissions,
            tolal_data=len(role_permissions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=RolePermissionPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_role_permission_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(RolePermission).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        role_permissions = db.query(RolePermission).offset(offset).limit(page_size).all()

        return RolePermissionPageableResponse(
            role_permissions=role_permissions,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{role_permission_id}", 
            response_model=RolePermissionResponse, 
            status_code=status.HTTP_200_OK)
async def search_role_permission_by_id(
        role_permission_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        role_permission = db.query(RolePermission).filter(RolePermission.id == role_permission_id).first()
        if not role_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Vai trò - quyền không tồn tại"
            )

        return role_permission
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/search",
            response_model=ListRolePermissionResponse)
async def search_role_permissions_by_name(
        info: RolePermissionSearch,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = db.query(RolePermission)
        if info.role_id:
            role_permissions = role_permissions.filter(RolePermission.role_id == info.role_id)
        if info.permission_id:
            role_permissions = role_permissions.filter(RolePermission.permission_id == info.permission_id)
        role_permissions = role_permissions.all()

        return ListRolePermissionResponse(
            role_permissions=role_permissions,
            tolal_data=len(role_permissions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create", 
             response_model=RolePermissionResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_role_permission(
        new_role_permission: RolePermissionCreate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permission = db.query(Permission).filter(Permission.id == new_role_permission.permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền không tồn tại"
            )
        
        role = db.query(Role).filter(Role.id == new_role_permission.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Vai trò không tồn tại"
            )
        
        role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == new_role_permission.role_id,
            RolePermission.permission_id == new_role_permission.permission_id
        ).first()

        if role_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Vai trò - Quyền đã tồn tại"
            )

        role_permission = RolePermission(**new_role_permission.dict())
        db.add(role_permission)
        db.commit()    

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Tạo vai trò - quyền thành công"}
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/import",
            response_model=list[RolePermissionResponse], 
            status_code=status.HTTP_201_CREATED)
async def import_role_permissions(
        role_permissions: list[RolePermissionCreate],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = [RolePermission(**role_permission.dict()) for role_permission in role_permissions]
        db.add_all(role_permissions)
        db.commit()

        return role_permissions
    
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.put("/update/{role_permission_id}", 
            response_model=RolePermissionResponse, 
            status_code=status.HTTP_200_OK)
async def update_role_permission(
        role_permission_id: int,
        new_role_permission: RolePermissionUpdate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permission = db.query(RolePermission).filter(RolePermission.id == role_permission_id)
        if not role_permission.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )

        role_permission.update(new_role_permission.dict())
        db.commit()

        return role_permission.first()
    
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete/{role_permission_id}", 
            status_code=status.HTTP_200_OK)
async def delete_role_permission(
        role_permission_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permission = db.query(RolePermission).filter(RolePermission.id == role_permission_id)
        if not role_permission.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        role_permission.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa quyền thành công"}
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-many",
               status_code=status.HTTP_200_OK)
async def delete_role_permissions(
        ids: list[int],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = db.query(RolePermission).filter(RolePermission.id.in_(ids))
        if not role_permissions.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        role_permissions.delete(synchronize_session=False)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa quyền thành công"}
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.delete("/delete-all",
               status_code=status.HTTP_200_OK)
async def delete_all_role_permissions(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(RolePermission).delete()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Xóa tất cả quyền thành công"}
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
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    