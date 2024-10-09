from fastapi import status, HTTPException
from .. import schemas, models, utils
from sqlalchemy.orm import Session


def get_author_by_id(author_id: int, 
                     db: Session):
    
    author = utils.query_author_by_id(db, author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found author")
    
    return author


def get_author_all(db: Session):
    
    authors = utils.query_author_all(db).all()
    
    return authors


def create_author(new_author: schemas.AuthorCreate, 
               db: Session, 
               current_user):
        
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author = models.Author(**new_author.dict())
    db.add(author)
    db.commit()
    
    return author


def update_author(author_id: int,
                  new_author: schemas.AuthorCreate, 
                  db: Session, 
                  current_user):
    author_query = utils.query_author_by_id(db, author_id)
    if not author_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author_query.update(new_author.dict(), synchronize_session=False)
    db.commit()
    
    return author_query.first()


def delete_author(author_id: int, 
                  db: Session, 
                  current_user):
    author_query = utils.query_author_by_id(db, author_id)
    if not author_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found")
     
    if current_user.role_id != utils.get_role_by_name(db, "admin").id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not permission")
    
    author_query.delete(synchronize_session=False)
    db.commit()
    
    return {"message": "Delete publisher succesfull"}


