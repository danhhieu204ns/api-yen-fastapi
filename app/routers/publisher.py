from fastapi import status, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, database, oauth2
from ..repository import publisher
from ..database import get_db


router = APIRouter(
    prefix="/publisher",
    tags=['Publishers']
)

@router.get("/all", 
            status_code=status.HTTP_200_OK, 
            response_model=List[schemas.PublisherResponse])
async def get_publisher_all(db: Session = Depends(database.get_db), 
                            limit: int = 5, 
                            skip: int = 0, 
                            search: Optional[str] = ''):
    
    return publisher.get_publisher_all(db, limit, skip, search)


@router.get("/pageable", 
            status_code=status.HTTP_200_OK)
async def get_publisher_pageable(page: int, 
                              page_size: int, 
                              db: Session = Depends(get_db)):
     
    return publisher.get_publisher_pageable(page, page_size, db)


@router.get("/{publisher_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.PublisherResponse)
async def get_publisher_by_id(publisher_id: int, 
                              db: Session = Depends(database.get_db)):

    return publisher.get_publisher_by_id(publisher_id, db)


@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.PublisherResponse)
async def create_publisher(new_publisher: schemas.PublisherCreate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return publisher.create_publisher(new_publisher, db, current_user)


@router.put("/update/{publisher_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.PublisherResponse)
async def update_publisher(publisher_id: int, 
                           new_publisher: schemas.PublisherUpdate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return publisher.update_publisher(publisher_id, new_publisher, db, current_user)


@router.delete("/delete/{publisher_id}", 
               status_code=status.HTTP_200_OK, )
async def delete_publisher(publisher_id: int, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return publisher.delete_publisher(publisher_id, db, current_user)


@router.delete("/delete-many", 
               status_code=status.HTTP_200_OK)
async def delete_many_publisher(publisher_ids: schemas.DeleteMany, 
                             db: Session = Depends(database.get_db), 
                             current_user = Depends(oauth2.get_current_user)):
    
    return publisher.delete_many_publisher(publisher_ids, db, current_user)
