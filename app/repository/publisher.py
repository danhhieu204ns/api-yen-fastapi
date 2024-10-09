from fastapi import status, HTTPException
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from typing import Optional


def get_publisher_all(db: Session, 
                        limit: int, 
                        skip: int, 
                        search: Optional[str]):
    
    publishers = utils.query_publisher_all(db, limit, skip, search).all()

    return publishers


def get_publisher_by_id(publisher_id: int, 
                      db: Session):
    
    publisher = utils.query_publisher_by_id(db, publisher_id).first()
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found publisher")
    
    return publisher


def create_publisher(new_publisher: schemas.PublisherCreate, 
                     db: Session, 
                     current_user):

    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")

    publisher = models.Publisher(**new_publisher.dict())
    db.add(publisher)
    db.commit()
    
    return publisher


def update_publisher(publisher_id: int,
                     new_publisher: schemas.PublisherUpdate, 
                     db: Session, 
                     current_user):
    publisher_query = utils.query_publisher_by_id(db, publisher_id)
    if not publisher_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found publisher")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    publisher_query.update(new_publisher.dict(), synchronize_session=False)
    db.commit()
    
    return publisher_query.first()


def delete_publisher(publisher_id: int, 
                  db: Session, 
                  current_user):
    publisher_query = utils.query_publisher_by_id(db, publisher_id)
    if not publisher_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found publisher")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    publisher_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete publisher succesfull"}