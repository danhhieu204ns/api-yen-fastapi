from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import schemas, database, oauth2
from ..repository import book


router = APIRouter(
    prefix="/book",
    tags=["Books"]
)

@router.get("/all", 
            response_model=List[schemas.BookResponse])
async def get_book_all(db: Session = Depends(database.get_db), 
                            limit: int = 5, 
                            skip: int = 0, 
                            search: Optional[str] = ''):
    
    return book.get_book_all(db, limit, skip, search)


@router.get("/{book_id}", 
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


# @router.put("/update/{book_id}", 
#             response_model=schemas.BookResponse, 
#             status_code=status.HTTP_200_OK)
# async def update_book(book_id: int, 
#                            new_book: schemas.BookCreate, 
#                            db: Session = Depends(database.get_db), 
#                            current_user = Depends(oauth2.get_current_user)):

#     return book.update_bookgroup(book_id, new_book, db, current_user)


@router.delete("/delete/{book_id}")
async def delete_book(book_id: int, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return book.delete_book(book_id, db, current_user)
