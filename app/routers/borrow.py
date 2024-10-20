from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import schemas, oauth2
from ..repository import borrow
from ..database import get_db


router = APIRouter(
    prefix="/borrow",
    tags=["Borrows"]
)

@router.get("/all", 
            status_code=status.HTTP_200_OK, 
            response_model=List[schemas.BorrowResponse])
async def get_borrow_all(db: Session = Depends(get_db), 
                         limit: int = 5, 
                         skip: int = 0, 
                         search: Optional[str] = ''):
    
    return borrow.get_borrow_all(db, limit, skip, search)


@router.get("/pageable", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BorrowPageableResponse)
async def get_borrow_pageable(page: int, 
                              page_size: int, 
                              db: Session = Depends(get_db)):
     
    return borrow.get_borrow_pageable(page, page_size, db)


@router.get("/{borrow_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BorrowResponse)
async def get_borrow_by_id(borrow_id: int, 
                           db: Session = Depends(get_db)):

    return borrow.get_borrow_by_id(borrow_id, db)


@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.BorrowResponse)
async def create_borrow(new_borrow: schemas.BorrowCreate, 
                        db: Session = Depends(get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    return borrow.create_borrow(new_borrow, db, current_user)


@router.put("/update/{borrow_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BorrowResponse)
async def update_borrow(borrow_id: int, 
                        new_borrow: schemas.BorrowUpdate, 
                        db: Session = Depends(get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    return borrow.update_borrow(borrow_id, new_borrow, db, current_user)


@router.delete("/delete/{borrow_id}", 
               status_code=status.HTTP_200_OK)
async def delete_borrow(borrow_id: int, 
                        db: Session = Depends(get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    return borrow.delete_borrow(borrow_id, db, current_user)



@router.delete("/delete-many", 
               status_code=status.HTTP_200_OK)
async def delete_many_borrow(borrow_ids: schemas.DeleteMany, 
                             db: Session = Depends(get_db), 
                             current_user = Depends(oauth2.get_current_user)):
    
    return borrow.delete_many_borrow(borrow_ids, db, current_user)
