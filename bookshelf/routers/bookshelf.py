from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from bookshelf.models.bookshelf import Bookshelf
from bookshelf.schemas.bookshelf import BookshelfCreate, BookshelfUpdate, BookshelfResponse, BookshelfPageableResponse, BookshelfImport
import math


router = APIRouter(
    prefix="/bookshelf",
    tags=["Bookshelf"],
)


@router.get("/all",
            response_model=list[BookshelfResponse],
            status_code=status.HTTP_200_OK)
async def get_bookshelfs(
        db: Session = Depends(get_db)
    ):

    try:
        bookshelfs = db.query(Bookshelf).all()

        return bookshelfs

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookshelfPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_bookshelf_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Bookshelf).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        bookshelfs = db.query(Bookshelf).offset(offset).limit(page_size).all()

        bookshelfs_pageable = BookshelfPageableResponse(
            total_count=total_count,
            total_pages=total_pages,
            bookshelfs=bookshelfs
        )

        return bookshelfs_pageable
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookshelfResponse,
            status_code=status.HTTP_200_OK)
async def search_bookshelf_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.id == id).first()
        if not bookshelf:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )
        
        return bookshelf
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=list[BookshelfResponse], 
            status_code=status.HTTP_200_OK)
async def search_bookshelfs_by_name(
        name: str,
        db: Session = Depends(get_db)
    ):

    try:
        bookshelfs = db.query(Bookshelf).filter(Bookshelf.name.ilike(f"%{name}%")).all()
        if not bookshelfs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )
        
        return bookshelfs
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=BookshelfResponse,
            status_code=status.HTTP_201_CREATED)
async def create_bookshelf(
        new_bookshelf: BookshelfCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.name == new_bookshelf.name).first()
        if bookshelf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tủ sách đã tồn tại"
            )

        bookshelf = Bookshelf(**new_bookshelf.dict())
        db.add(bookshelf)
        db.commit()

        return bookshelf
    
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
            response_model=list[BookshelfResponse],
            status_code=status.HTTP_201_CREATED)
async def import_bookshelfs(
        bookshelfs: BookshelfImport,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelfs_db = [Bookshelf(**book.dict()) for book in bookshelfs.bookshelfs]
        db.add_all(bookshelfs_db)
        db.commit()

        return bookshelfs_db
    
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


@router.put("/update/{id}",
            response_model=BookshelfResponse,
            status_code=status.HTTP_200_OK)
async def update_bookshelf(
        id: int,
        bookshelf: BookshelfUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf_db = db.query(Bookshelf).filter(Bookshelf.id == id)
        if not bookshelf_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelf_db.update(bookshelf.dict(), 
                            synchronize_session=False)
        db.commit()

        return bookshelf_db.first()
    
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


@router.delete("/delete/{id}",
            status_code=status.HTTP_200_OK)
async def delete_bookshelf(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelf = db.query(Bookshelf).filter(Bookshelf.id == id)
        if not bookshelf.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelf.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa tủ sách thành công"}
    
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
async def delete_bookshelfs(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        bookshelfs = db.query(Bookshelf).filter(Bookshelf.id.in_(ids))
        if not bookshelfs.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tủ sách không tồn tại"
            )

        bookshelfs.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa danh sách tủ sách thành công"}
    
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
async def delete_all_bookshelfs(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Bookshelf).delete()
        db.commit()

        return {"message": "Xóa tất cả tủ sách thành công"}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )
