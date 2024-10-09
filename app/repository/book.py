from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models, utils



def get_book_all(db: Session, 
                  limit: int, 
                  skip: int, 
                  search: Optional[str]):
    
    bookgroups = utils.query_book_all(db, limit, skip, search).all()

    return bookgroups


def get_book_by_id(book_id: int, 
                    db: Session):
    
    book = utils.query_book_by_id(db, book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found book")
    
    return book


def create_book(new_book: schemas.BookCreate, 
                 db: Session, 
                 current_user):

    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    if not utils.query_bookgroup_by_id(db, new_book.bookgroup_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found groupbook")
    
    book = models.Book(**new_book.dict())
    db.add(book)
    db.commit()
    
    return book


def update_book(book_id: int,
                     new_book: schemas.BookUpdate, 
                     db: Session, 
                     current_user):
    book_query = utils.query_book_by_id(db, book_id)
    if not book_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found book")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    book_query.update(new_book.dict(), synchronize_session=False)
    db.commit()
    
    return book_query.first()


def delete_book(book_id: int, 
                 db: Session, 
                 current_user):
    book_query = utils.query_book_by_id(db, book_id)
    if not book_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found book")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    book_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete book succesfull"}