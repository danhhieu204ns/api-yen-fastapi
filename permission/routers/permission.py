from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from permission.models.permission import Permission
from permission.schemas.permission import *
import math


router = APIRouter(
    prefix="/permission",
    tags=["Permission"],
)


@router.get("/all", 
            response_model=ListPermissionResponse, 
            status_code=status.HTTP_200_OK)
async def get_permissions(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        permissions = db.query(Permission).all()

        return ListPermissionResponse(
            permissions=permissions, 
            tolal_data=len(permissions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=PermissionPageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_permission_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(Permission).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        permissions = db.query(Permission).offset(offset).limit(page_size).all()

        return PermissionPageableResponse(
            permissions=permissions,
            total_pages=total_pages,
            total_data=total_count
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{permission_id}", 
            response_model=PermissionResponse, 
            status_code=status.HTTP_200_OK)
async def get_permission_by_id(
        permission_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Quyền không tồn tại"
            )
        
        return permission
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search",
            response_model=ListPermissionResponse)
async def search_permissions_by_name(
        info: PermissionSearch,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permissions = db.query(Permission)
        if info.name:
            permissions = permissions.filter(Permission.name.like(f"%{info.name}%"))
        if info.detail:
            permissions = permissions.filter(Permission.detail.like(f"%{info.detail}%"))
        permissions = permissions.all()

        return ListPermissionResponse(
            permissions=permissions,
            tolal_data=len(permissions)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create", 
             response_model=PermissionResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_permission(
        new_permission: PermissionCreate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permission = db.query(Permission).filter(Permission.name == new_permission.name).first()
        if permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền đã tôn tại"
            )

        permission = Permission(**new_permission.dict())
        db.add(permission)
        db.commit()    

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Tạo quyền thành công"}
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
            response_model=list[PermissionResponse], 
            status_code=status.HTTP_201_CREATED)
async def import_permissions(
        permissions: list[PermissionCreate],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permissions = [Permission(**permission.dict()) for permission in permissions]
        db.add_all(permissions)
        db.commit()

        return permissions
    
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


@router.put("/update/{permission_id}", 
            response_model=PermissionResponse, 
            status_code=status.HTTP_200_OK)
async def update_permission(
        permission_id: int,
        new_permission: PermissionUpdate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permission = db.query(Permission).filter(Permission.id == permission_id)
        if not permission.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )

        permission.update(new_permission.dict())
        db.commit()

        return permission.first()
    
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


@router.delete("/delete/{permission_id}", 
            status_code=status.HTTP_200_OK)
async def delete_permission(
        permission_id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permission = db.query(Permission).filter(Permission.id == permission_id)
        if not permission.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        permission.delete(synchronize_session=False)
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
async def delete_roles(
        permission_ids: list[int],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids))
        if not permissions.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền không tồn tại"
            )
        permissions.delete(synchronize_session=False)
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
async def delete_all_permissions(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Permission).delete()
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
    