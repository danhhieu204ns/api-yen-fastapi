from fastapi import status, APIRouter, Depends
from .. import schemas, database, oauth2
from ..repository import publisher
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(
    prefix="/publisher",
    tags=['Publishers']
)

@router.get("/all", 
            response_model=List[schemas.PublisherResponse])
async def get_publisher_all(db: Session = Depends(database.get_db), 
                            limit: int = 5, 
                            skip: int = 0, 
                            search: Optional[str] = ''):
    
    return publisher.get_publisher_all(db, limit, skip, search)


@router.get("/{publisher_id}", 
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
            response_model=schemas.PublisherResponse, 
            status_code=status.HTTP_200_OK)
async def update_publisher(publisher_id: int, 
                           new_publisher: schemas.PublisherUpdate, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return publisher.update_publisher(publisher_id, new_publisher, db, current_user)


@router.delete("/delete/{publisher_id}")
async def delete_publisher(publisher_id: int, 
                           db: Session = Depends(database.get_db), 
                           current_user = Depends(oauth2.get_current_user)):

    return publisher.delete_publisher(publisher_id, db, current_user)


