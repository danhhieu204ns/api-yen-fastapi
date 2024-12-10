import math
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from role_permission.models.role_permission import RolePermission
from role_permission.schemas.role_permission import RolePermissionCreate, RolePermissionResponse, RolePermissionUpdate, RolePermissionPageableResponse


router = APIRouter(
    prefix="/role-permission",
    tags=["Role_Permission"],
)


@router.get("/all", 
            response_model=list[RolePermissionResponse], 
            status_code=status.HTTP_200_OK)
async def get_role_permissions(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = db.query(RolePermission).all()

        return role_permissions
    
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

        role_permissions_pageable_res = RolePermissionPageableResponse(
            role_permissions=role_permissions,
            total_pages=total_pages,
            total_data=total_count
        )

        return role_permissions_pageable_res
    
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
                detail=f"Quyền không tồn tại"
            )

        return role_permission
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=list[RolePermissionResponse],)
async def search_role_permissions_by_name(
        name: str,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role_permissions = db.query(RolePermission).filter(RolePermission.name.like(f"%{name}%")).all()
        if not role_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Quyền không tồn tại"
            )

        return role_permissions
    
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
        role_permission = db.query(RolePermission).filter(RolePermission.name == new_role_permission.name).first()
        if role_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Quyền đã tôn tại"
            )

        role_permission = RolePermission(**new_role_permission.dict())
        db.add(role_permission)
        db.commit()    

        return role_permission
    
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

        return {"message": "Xóa quyền thành công"}
    
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

        return {"message": "Xóa quyền thành công"}
    
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

        return {"message": "Xóa tất cả quyền thành công"}
    
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
    