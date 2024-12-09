from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from role.models.role import Role
from role.schemas.role import RoleResponse, RoleCreate, RoleUpdate, RolePageableResponse
import math


router = APIRouter(
    prefix="/role",
    tags=["Role"],
)


@router.get("/all", 
            response_model=list[RoleResponse], 
            status_code=status.HTTP_200_OK)
async def get_roles(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        roles = db.query(Role).all()

        return roles
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=RolePageableResponse, 
            status_code=status.HTTP_200_OK)
async def get_roles_pageable(
        page: int, 
        page_size: int, 
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
     
    try:
        total_count = db.query(Role).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        roles = db.query(Role).offset(offset).limit(page_size).all()

        roles_pageable_res = RolePageableResponse(
            roles=roles,
            total_pages=total_pages,
            total_data=total_count
        )

        return roles_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}", 
            response_model=RoleResponse, 
            status_code=status.HTTP_200_OK)
async def search_role_by_id(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):
    
    try:
        role = db.query(Role).filter(Role.id == id).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Quyền không tồn tại")

        return role
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=list[RoleResponse])
async def search_roles_by_name(
        name: str,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        roles = db.query(Role).filter(Role.name.like(f"%{name}%")).all()
        if not roles:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Quyền không tồn tại")

        return roles
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create", 
             response_model=RoleResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_role(
        new_role: RoleCreate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role = db.query(Role).filter(Role.name == new_role.name).first()
        if role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Quyền đã tôn tại")

        role = Role(**new_role.dict())
        db.add(role)
        db.commit()    

        return role
    
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
            response_model=list[RoleResponse], 
            status_code=status.HTTP_201_CREATED)
async def import_roles(
        roles: list[RoleCreate],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        roles = [Role(**role.dict()) for role in roles]
        db.add_all(roles)
        db.commit()

        return roles
    
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


@router.put("/{id}/update", 
            response_model=RoleResponse, 
            status_code=status.HTTP_200_OK)
async def update_role(
        id: int,
        new_role: RoleUpdate,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role = db.query(Role).filter(Role.id == id)
        if not role.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Quyền không tồn tại")

        role.update(new_role.dict())
        db.commit()

        return role.first()
    
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


@router.delete("/{id}/delete", 
            status_code=status.HTTP_200_OK)
async def delete_role(
        id: int,
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        role = db.query(Role).filter(Role.id == id)
        if not role.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Quyền không tồn tại")
        role.delete(synchronize_session=False)
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
async def delete_roles(
        ids: list[int],
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        roles = db.query(Role).filter(Role.id.in_(ids))
        if not roles.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Quyền không tồn tại")
        roles.delete(synchronize_session=False)
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
async def delete_all_roles(
        db: Session = Depends(get_db), 
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Role).delete()
        db.commit()

        return {"message": "Xóa tất cả quyền thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    