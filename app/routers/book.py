from fastapi import Form, status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import schemas, database, oauth2
from ..repository import book
from ..database import get_db


router = APIRouter(
    prefix="/book",
    tags=["Books"]
)

@router.get("/all", 
            status_code=status.HTTP_200_OK, 
            response_model=List[schemas.BookResponse])
async def get_book_all(db: Session = Depends(database.get_db), 
                            search: Optional[str] = ''):
    
    return book.get_book_all(db)


@router.get("/pageable", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BookPageableResponse)
async def get_book_pageable(page: int, 
                              page_size: int, 
                              db: Session = Depends(get_db)):
     
    return book.get_book_pageable(page, page_size, db)


@router.get("/{book_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BookResponse)
async def get_book_by_id(book_id: int, 
                          db: Session = Depends(database.get_db)):

    return book.get_book_by_id(book_id, db)


@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.BookResponse)
async def create_book(new_book: schemas.BookCreate, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return book.create_book(new_book, db, current_user)


@router.put("/update/{book_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BookResponse)
async def update_book(book_id: int, 
                           new_book: schemas.BookCreate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return book.update_book(book_id, new_book, db, current_user)


@router.delete("/delete/{book_id}", 
               status_code=status.HTTP_200_OK, )
async def delete_book(book_id: int, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return book.delete_book(book_id, db, current_user)



@router.delete("/delete-many", 
               status_code=status.HTTP_200_OK)
async def delete_many_book(book_ids: schemas.DeleteMany, 
                             db: Session = Depends(database.get_db), 
                             current_user = Depends(oauth2.get_current_user)):
    
    return book.delete_many_book(book_ids, db, current_user)


@router.post("/check", 
               status_code=status.HTTP_200_OK, 
               response_model=schemas.BookResponse)
async def check_book(book_img: str = Form(...), 
                    db: Session = Depends(database.get_db), 
                    current_user = Depends(oauth2.get_current_user)):
    
    return book.check_book(book_img, db, current_user)