from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from configs.authentication import get_current_user
from configs.database import get_db
from book.models.book import Book
from book.schemas.book import BookCreate, BookResponse, BookUpdate, BookPageableResponse, BookImport
import math


router = APIRouter(
    prefix="/book",
    tags=["Book"],
)


@router.get("/all",
            response_model=list[BookResponse],
            status_code=status.HTTP_200_OK)
async def get_books(
        db: Session = Depends(get_db)
    ):

    try:
        books = db.query(Book).all()

        return books

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/pageable",
            response_model=BookPageableResponse,
            status_code=status.HTTP_200_OK)
async def get_genres_pageable(
        page: int,
        page_size: int,
        db: Session = Depends(get_db)
    ):

    try:
        total_count = db.query(Book).count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        books = db.query(Book).offset(offset).limit(page_size).all()

        books_pageable = BookPageableResponse(
            total_count=total_count,
            total_pages=total_pages,
            books=books
        )

        return books_pageable
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/{id}",
            response_model=BookResponse,
            status_code=status.HTTP_200_OK)
async def search_book_by_id(
        id: int,
        db: Session = Depends(get_db)
    ):

    try:
        book = db.query(Book).filter(Book.id == id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )
        
        return book
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.get("/search/by-name/{name}",
            response_model=list[BookResponse], 
            status_code=status.HTTP_200_OK)
async def search_books_by_name(
        name: str,
        db: Session = Depends(get_db)
    ):

    try:
        books = db.query(Book).filter(Book.name.ilike(f"%{name}%")).all()
        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )
        
        return books
    
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi cơ sở dữ liệu: {str(e)}"
        )


@router.post("/create",
            response_model=BookResponse,
            status_code=status.HTTP_201_CREATED)
async def create_book(
        new_book: BookCreate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book = db.query(Book).filter(Book.name == new_book.name).first()
        if book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sách đã tồn tại"
            )

        book = Book(**new_book.dict())
        db.add(book)
        db.commit()

        return book
    
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
            response_model=list[BookResponse],
            status_code=status.HTTP_201_CREATED)
async def import_books(
        books: BookImport,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        books_db = [Book(**book.dict()) for book in books.books]
        db.add_all(books_db)
        db.commit()

        return books_db
    
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
            response_model=BookResponse,
            status_code=status.HTTP_200_OK)
async def update_book(
        id: int,
        book: BookUpdate,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book_db = db.query(Book).filter(Book.id == id)
        if not book_db.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        book_db.update(book.dict(), synchronize_session=False)
        db.commit()

        return book_db.first()
    
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
async def delete_book(
        id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        book = db.query(Book).filter(Book.id == id)
        if not book.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        book.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa sách thành công"}
    
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
async def delete_books(
        ids: list[int],
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        books = db.query(Book).filter(Book.id.in_(ids))
        if not books.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sách không tồn tại"
            )

        books.delete(synchronize_session=False)
        db.commit()

        return {"message": "Xóa danh sách sách thành công"}
    
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
async def delete_all_books(
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):

    try:
        db.query(Book).delete()
        db.commit()

        return {"message": "Xóa tất cả sách thành công"}
    
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
    