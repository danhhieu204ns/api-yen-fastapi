from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models, utils
import math



def get_book_all(db: Session):
    
    books = utils.query_book_all(db).all()

    return books


def get_book_by_id(book_id: int, 
                        db: Session):
    
    book = utils.query_book_by_id(db, book_id).first()
    
    return book


def get_book_pageable(
    page: int, 
    page_size: int, 
    db: Session
):
    total_count = db.query(models.Book).count()
    total_pages = math.ceil(total_count / page_size)
    offset = (page - 1) * page_size
    books = db.query(models.Book).offset(offset).limit(page_size).all()

    book_pageable_res = schemas.BookPageableResponse(
        books=books,
        total_pages=total_pages,
        total_data=total_count
    )

    return book_pageable_res


def create_book(
    new_book: schemas.BookCreate, 
    db: Session, 
    current_user
):
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")

    book = models.Book(**new_book.dict())
    db.add(book)
    db.commit()
    
    return book


def update_book(
    book_id: int,
    new_book: schemas.BookUpdate, 
    db: Session, 
    current_user
):
    book_query = utils.query_book_by_id(db, book_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    book_query.update(new_book.dict(), synchronize_session=False)
    db.commit()
    
    return book_query.first()


def delete_book(
    book_id: int, 
    db: Session, 
    current_user
): 
    book_query = utils.query_book_by_id(db, book_id)
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    book_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete book succesfull"}


def delete_many_book(
    book_ids: schemas.DeleteMany, 
    db: Session, 
    current_user
):
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Không có quyền thực hiện thao tác này")

    book_query = db.query(models.Book).filter(models.Book.id.in_(book_ids.list_id))

    if book_query.count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Không tìm thấy book với các ID đã cung cấp")

    book_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Xóa danh sách book thành công"}
