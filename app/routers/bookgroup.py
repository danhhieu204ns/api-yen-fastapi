from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import schemas, database, oauth2
from ..repository import bookgroup
from ..database import get_db


router = APIRouter(
    prefix="/bookgroup",
    tags=["Bookgroups"]
)

@router.get("/all", 
            response_model=List[schemas.BookgroupResponse])
async def get_bookgroup_all(db: Session = Depends(database.get_db), 
                            limit: int = 5, 
                            skip: int = 0, 
                            search: Optional[str] = ''):
    
    return bookgroup.get_bookgroup_all(db, limit, skip, search)


@router.get("/pageable", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.BookgroupPageableResponse)
async def get_bookgroup_pageable(page: int, 
                              page_size: int, 
                              db: Session = Depends(get_db)):
     
    return bookgroup.get_bookgroup_pageable(page, page_size, db)


@router.get("/{bookgroup_id}", 
            response_model=schemas.BookgroupResponse)
async def get_bookgroup_by_id(bookgroup_id: int, 
                          db: Session = Depends(database.get_db)):

    return bookgroup.get_bookgroup_by_id(bookgroup_id, db)


@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.BookgroupResponse)
async def create_bookgroup(new_bookgroup: schemas.BookgroupCreate, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return bookgroup.create_bookgroup(new_bookgroup, db, current_user)


@router.put("/update/{bookgroup_id}", 
            response_model=schemas.BookgroupResponse, 
            status_code=status.HTTP_200_OK)
async def update_bookgroup(bookgroup_id: int, 
                           new_bookgroup: schemas.BookgroupCreate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return bookgroup.update_bookgroup(bookgroup_id, new_bookgroup, db, current_user)


@router.delete("/delete/{bookgroup_id}")
async def delete_bookgroup(bookgroup_id: int, 
                       db: Session = Depends(database.get_db), 
                       current_user = Depends(oauth2.get_current_user)):

    return bookgroup.delete_bookgroup(bookgroup_id, db, current_user)



@router.delete("/delete-many", 
               status_code=status.HTTP_200_OK)
async def delete_many_bookgroup(bookgroup_ids: schemas.DeleteMany, 
                             db: Session = Depends(database.get_db), 
                             current_user = Depends(oauth2.get_current_user)):
    
    return bookgroup.delete_many_bookgroup(bookgroup_ids, db, current_user)
