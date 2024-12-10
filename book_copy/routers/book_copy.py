from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from book_copy.models.book_copy import BookCopy
from book_copy.schemas.book_copy import BookCopyCreate, BookCopyUpdate, BookCopyResponse, BookCopyPageableResponse, BookCopyImport
import math


router = APIRouter(
    prefix="/book-copies",
    tags=["Book_Copies"],
)


@router.get("/all",
            response_model=list[BookCopyResponse],
            status_code=status.HTTP_200_OK)
async def get_book_copies(
        db: Session = Depends(get_db)
    ):

    try:
        book_copies = db.query(BookCopy).all()

        return book_copies

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookCopyPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_book_copy_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(BookCopy).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        book_copies = db.query(BookCopy).offset(offset).limit(page_size).all()

        book_copies_pageable = BookCopyPageableResponse(
            total_count=total_count,
            total_pages=total_pages,
            book_copies=book_copies
        )

        return book_copies_pageable
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookCopyResponse,
            status_code=status.HTTP_200_OK)
async def search_book_copy_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        book_copy = db.query(BookCopy).filter(BookCopy.id == id).first()
        if not book_copy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )
        
        return book_copy
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=BookCopyResponse,
            status_code=status.HTTP_201_CREATED)
async def create_book_copy(
        new_book_copy: BookCopyCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy = BookCopy(**new_book_copy.dict())
        db.add(book_copy)
        db.commit()

        return book_copy
    
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
            response_model=list[BookCopyResponse],
            status_code=status.HTTP_201_CREATED)
async def import_book_copies(
        book_copies: BookCopyImport,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copies_db = [BookCopy(**book_copy.dict()) for book_copy in book_copies.book_copies]
        db.add_all(book_copies_db)
        db.commit()

        return book_copies_db
    
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
            response_model=BookCopyResponse,
            status_code=status.HTTP_200_OK)
async def update_book_copy(
        id: int,
        book_copy: BookCopyUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy_db = db.query(BookCopy).filter(BookCopy.id == id)
        if not book_copy_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copy_db.update(book_copy.dict(), 
                            synchronize_session=False)
        db.commit()

        return book_copy_db.first()
    
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
async def delete_book_copy(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copy = db.query(BookCopy).filter(BookCopy.id == id)
        if not book_copy.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copy.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa bản sao sách thành công"}
    
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
async def delete_book_copies(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_copies = db.query(BookCopy).filter(BookCopy.id.in_(ids))
        if not book_copies.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bản sao sách không tồn tại"
            )

        book_copies.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa danh sách bản sao sách thành công"}
    
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
async def delete_all_book_copies(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(BookCopy).delete()
        db.commit()

        return {"message": "Xóa tất cả bản sao sách thành công"}
    
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
