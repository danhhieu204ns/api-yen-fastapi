from fastapi import status, Depends, APIRouter
from typing import List, Optional
from .. import schemas, oauth2
from ..database import get_db
from ..repository import author
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= "/author",
    tags=["Authors"]
)


@router.get("/all", 
            status_code=status.HTTP_200_OK, 
            response_model=list[schemas.AuthorResponse])
async def get_author_by_id(db: Session = Depends(get_db)):
    
    return author.get_author_all(db)


@router.get("/pageable", 
            status_code=status.HTTP_200_OK)
async def get_author_pageable(page: int, 
                              page_size: int, 
                              db: Session = Depends(get_db)):
     
    return author.get_author_pageable(page, page_size, db)


@router.get("/{author_id}", 
            status_code=status.HTTP_200_OK, 
            response_model=schemas.AuthorResponse)
async def get_author_all(author_id: int, 
                         db: Session = Depends(get_db)):
    
    return author.get_author_by_id(author_id, db)
    

@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.AuthorResponse)
async def create_author(new_author: schemas.AuthorCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
    return author.create_author(new_author, db, current_user)


@router.put("/update/{author_id}", 
            status_code=status.HTTP_202_ACCEPTED, 
            response_model=schemas.AuthorResponse)
async def update_author(author_id: int,
                        author_info: schemas.AuthorCreate, 
                        db: Session = Depends(get_db), 
                        current_user = Depends(oauth2.get_current_user)):
    
    return author.update_author(author_id, author_info, db, current_user)


@router.delete("/delete/{author_id}", 
               status_code=status.HTTP_200_OK)
async def delete_author(author_id: int, 
                        db: Session = Depends(get_db), 
                        current_user = Depends(oauth2.get_current_user)):
    
    return author.delete_author(author_id, db, current_user)


@router.delete("/delete-many", 
               status_code=status.HTTP_200_OK)
async def delete_many_author(author_ids: schemas.DeleteMany, 
                             db: Session = Depends(get_db), 
                             current_user = Depends(oauth2.get_current_user)):
    
    return author.delete_many_author(author_ids, db, current_user)
