from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from category.models.category import Category
from category.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate, CategoryPageableResponse
import math


router = APIRouter(
    prefix="/category",
    tags=["Category"],
)


@router.get("/all",
            response_model=list[CategoryResponse],
            status_code=status.HTTP_200_OK)
async def get_categories(
        db: Session = Depends(get_db)
    ):

    try:
        categories = db.query(Category).all()
        
        return categories
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=CategoryPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_categories_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Category).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        categories = db.query(Category).offset(offset).limit(page_size).all()

        categories_pageable_res = CategoryPageableResponse(
            categories=categories,
            total_pages=total_pages,
            total_data=total_count
        )

        return categories_pageable_res
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
    

@router.get("/{id}",
            response_model=CategoryResponse,
            status_code=status.HTTP_200_OK)
async def search_category_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        category = db.query(Category).filter(Category.id == id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        return category
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=CategoryResponse,
            status_code=status.HTTP_200_OK)
async def search_category_by_name(
        name: str,
        db: Session = Depends(get_db)
    ):

    try:
        category = db.query(Category).filter(Category.name.ilike(f"%{name}%")).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        return category
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=CategoryResponse,
            status_code=status.HTTP_201_CREATED)
async def create_category(
        new_category: CategoryCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category = db.query(Category).filter(Category.name == new_category.name).first()
        if category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại đã tồn tại"
            )

        category = Category(**new_category.dict())
        db.add(category)
        db.commit()

        return category
    
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
            response_model=list[CategoryResponse],
            status_code=status.HTTP_201_CREATED)
async def import_categories(
        categories: list[CategoryCreate],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        categories_db = []
        for category in categories:
            category_db = db.query(Category).filter(Category.name == category.name).first()
            if category_db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Thể loại đã tồn tại"
                )

            category_db = Category(**category.dict())
            db.add(category_db)
            categories_db.append(category_db)

        db.commit()

        return categories_db
    
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
            response_model=CategoryResponse,
            status_code=status.HTTP_200_OK)
async def update_category(
        id: int,
        category: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category_db = db.query(Category).filter(Category.id == id)
        if not category_db.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        category_db.update(category.dict(), 
                        synchronize_session=False)
        db.commit()

        return category_db.first()
    
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
async def delete_category(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        category = db.query(Category).filter(Category.id == id)
        if not category.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        category.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa thể loại thành công"}
    
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
async def delete_categories(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        categories = db.query(Category).filter(Category.id.in_(ids))
        if not categories.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thể loại không tồn tại"
            )

        categories.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa danh sách thể loại thành công"}
    
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
async def delete_all_categories(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Category).delete()
        db.commit()

        return {"message": "Xóa tất cả thể loại thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
